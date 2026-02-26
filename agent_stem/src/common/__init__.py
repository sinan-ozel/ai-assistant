from pathlib import Path

DEFAULTS_FOLDER = Path("/app/default")
CUSTOMIZATION_FOLDER = Path("/app/cortex")

# Available provider names
PROVIDER_NAMES = [
    "large",
    "small",
    "default",
    "vision",
    "coding",
    "reasoning",
    "evaluation",
    "instruction-following",
]
