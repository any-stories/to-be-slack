from pathlib import Path
from collections.abc import Mapping
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

BASE_DIR = Path(__file__).resolve().parent.parent / "templates"

class MessageRenderer:
    def __init__(self, template_path: str | Path = BASE_DIR):
        self.env = Environment(
            loader=FileSystemLoader(str(template_path)),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def render(self, template_name: str, context: Mapping) -> str:
        try:
            template = self.env.get_template(template_name)
        except TemplateNotFound:
            raise ValueError(f"Template '{template_name}' not found in template path.")
        return template.render(**context)