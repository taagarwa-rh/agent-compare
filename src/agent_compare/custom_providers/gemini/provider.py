import logging
import os
from pathlib import Path

from agent_compare.custom_providers.core import CustomProvider

logger = logging.getLogger(__name__)

GEMINI_ENVVARS = [
    "GOOGLE_CLOUD_PROJECT",
]


class CustomGeminiProvider(CustomProvider):
    """Custom gemini provider config."""

    name: str = "gemini_custom"

    def __init__(self):
        """Initialize."""
        parent_dir = Path(__file__).resolve().parent
        args = ["--from", str(parent_dir)]
        env = os.environ.copy()
        export_vals = "\n".join([f"export {var}={env[var]}" for var in GEMINI_ENVVARS])
        shell_cmds = ["bash", "-c", f"cat >> ~/.bashrc << 'EOF'\n{export_vals}\nEOF"]
        super().__init__(args=args, shell_cmds=shell_cmds)

    def create(self):
        """Create a Gemini provider."""
        self.openshell.provider_create(name=self.name)
