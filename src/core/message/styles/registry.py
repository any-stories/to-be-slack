from core.enums.message_style import MessageStyle
from core.message.models.pack import MessagePack
from core.message.styles.presets.default_style import DEFAULT_STYLE
from core.message.styles.presets.poetic_style import POETIC_STYLE
from core.message.styles.presets.romantic_style import ROMANTIC_STYLE

STYLE_REGISTRY: dict[
    MessageStyle,
    tuple[
        MessagePack,
        str,
    ],
] = {
    MessageStyle.DEFAULT: (
        DEFAULT_STYLE,
        "message_wecom_md.jinja2",
    ),
    MessageStyle.ROMANTIC: (
        ROMANTIC_STYLE,
        "message_romantic.jinja2",
    ),
    MessageStyle.POETIC: (
        POETIC_STYLE,
        "message_poetic.jinja2",
    ),
}
