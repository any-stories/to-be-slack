import datetime
import json
import random
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo
import yaml
from config import settings
from core.message_builder import MessageContextBuilder
from core.message_renderer import MessageRenderer
from notification.channel.wecom import WeComBot, WeComMarkdown
from utils.cron_util import CronUtil
from utils.holiday_util import HolidayUtil
from utils.logger import log

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = PROJECT_ROOT / ".state" / "state.json"
WORKFLOW_YAML = PROJECT_ROOT / ".github" / "workflows" / "schedule-slack.yml"

MAX_RECORDS = 7

# UTC+8 datetime.timezone(datetime.timedelta(hours=8))
BUSINESS_TZ = ZoneInfo("Asia/Shanghai")


def load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError) as e:
        log.warning(f"Failed to parse state file: {e}, returning empty dict.")
        return {}


def save_state(state: dict[str, Any]) -> None:
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except IOError as e:
        log.error(f"Failed to save state: {e}")


def has_executed_today(state: dict[str, Any], current_time: datetime.datetime) -> bool:
    today = current_time.date()

    for record in state.get("run_history", []):
        try:
            record_date = datetime.datetime.fromisoformat(record["timestamp"]).date()
            if record_date == today:
                return True
        except (ValueError, KeyError):
            continue

    return False


def record_run(state: dict[str, Any]) -> None:
    history = state.get("run_history", [])
    history.append({"timestamp": datetime.datetime.now().isoformat()})
    state["run_history"] = history[-MAX_RECORDS:]
    save_state(state)


def extract_workflow_crons() -> list[str]:
    if not WORKFLOW_YAML.exists():
        log.warning(f"Workflow file not found at {WORKFLOW_YAML}")
        return []
    try:
        with WORKFLOW_YAML.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            # Compatible 'on'  True
            on_config = data.get("on") or data.get(True) or {}
            schedules = on_config.get("schedule", [])
            return [
                s.get("cron") for s in schedules if isinstance(s, dict) and "cron" in s
            ]
    except Exception as e:
        log.warning(f"Error parsing YAML: {e}")
        return []


def in_do_not_disturb_period(current_time: datetime.datetime) -> bool:
    return settings.do_not_disturb_period and settings.do_not_disturb_period.is_active(
        current_time
    )


def is_last_chance_today(crons: list[str], current_time: datetime.datetime) -> bool:
    if current_time is None:
        raise ValueError("Current time cannot be None")
    if not crons:
        return True
    for cron in crons:
        next_time = CronUtil.get_next_time(cron, current_time)
        next_time_biz = next_time.astimezone(BUSINESS_TZ)
        # DND
        if in_do_not_disturb_period(next_time_biz):
            continue
        # next_time > current_time
        if next_time.date() == current_time.date():
            return False
    return True


def run() -> None:
    now_utc = datetime.datetime.now(datetime.UTC)
    system_time = now_utc.astimezone()
    business_time = now_utc.astimezone(BUSINESS_TZ)
    log.info(
        f"System time: {system_time.isoformat()} | "
        f"Business time: {business_time.isoformat()} ({business_time:%A})"
    )

    if in_do_not_disturb_period(business_time):
        log.info(
            f"Current time {business_time.time()} is in DND period ({settings.do_not_disturb_period.start}-{settings.do_not_disturb_period.end}). Skipping."
        )
        return

    today = business_time.date()
    today_status = HolidayUtil.get_day_status(today)
    if not today_status.get("is_workday", False):
        log.info(f"Today ({today} is not a workday. skipping.")
        return

    state = load_state()

    if not settings.once_per_day:
        log.warning("ONCE_PER_DAY is disabled, running...")
        if notify(today_status, business_time):
            record_run(state)
            log.info("Task executed successfully.")
        else:
            log.warning(f"Task execution failed.")
        return

    if has_executed_today(state, system_time):
        log.info("Task has already executed today. Skipping.")
        return

    crons = extract_workflow_crons()
    log.info(f"Extracted {len(crons)} cron schedules from workflow YAML.")

    should_execute = False

    if bool(random.getrandbits(1)):
        log.info("Task decision: running task now.")
        should_execute = True
    elif is_last_chance_today(crons, system_time):
        log.info("Task decision: Last execution slot for today. Forced run.")
        should_execute = True
    else:
        # Waiting for next scheduled execution
        log.info("Task decision: skipped for now, waiting for next scheduled slot.")

    if should_execute:
        if notify(today_status, business_time):
            record_run(state)
            log.info("Task executed successfully.")
        else:
            log.warning(f"Task execution failed.")


def notify(today_status: dict[str, Any], business_time: datetime.datetime) -> bool:
    try:
        context = MessageContextBuilder.build(
            today_status=today_status, business_time=business_time, settings=settings
        )

        renderer = MessageRenderer()
        message = renderer.render("message_wecom_md.jinja2", context)
        # log.info(f"Rendered message: {message}")

        result = WeComBot(settings.wecom_bot.key).send(WeComMarkdown(content=message))

        if result.success:
            log.info(result.msg)
        return result.success
    except Exception as e:
        log.exception(f"Unexpected error in notify: {str(e)}")
        return False


if __name__ == "__main__":
    run()
