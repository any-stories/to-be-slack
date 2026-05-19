from pathlib import Path

from collections.abc import Mapping

from jinja2 import (
    Environment,
    FileSystemLoader,
    TemplateNotFound,
)


def resolve_template_dir() -> Path:

    current_file = Path(__file__).resolve()
    src_dir = current_file.parent.parent.parent
    template_dir = src_dir / "templates"
    
    if template_dir.exists() and template_dir.is_dir():
        return template_dir

    raise RuntimeError("templates directory not found.")


TEMPLATE_DIR = resolve_template_dir()


class MessageRenderer:

    def __init__(
        self,
        template_path: Path = TEMPLATE_DIR,
    ):

        self.env = Environment(
            loader=FileSystemLoader(str(template_path)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(
        self,
        template_name: str,
        context: Mapping,
    ) -> str:

        try:
            template = self.env.get_template(template_name)
        except TemplateNotFound as e:
            raise ValueError(f"Template '{template_name}' not found.") from e
        return template.render(**context)
