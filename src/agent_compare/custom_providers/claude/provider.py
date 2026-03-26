import logging
import os
from pathlib import Path

from agent_compare.custom_providers.core.provider import CustomProvider

logger = logging.getLogger(__name__)

CLAUDE_ENVVARS = [
    "CLAUDE_CODE_USE_VERTEX",
    "CLOUD_ML_REGION",
    "ANTHROPIC_VERTEX_PROJECT_ID",
    "ANTHROPIC_MODEL",
    "ANTHROPIC_SMALL_FAST_MODEL",
]


class CustomClaudeProvider(CustomProvider):
    """Claude custom provider."""

    name: str = "claude_custom"

    def __init__(self):
        """Initialize."""
        parent_dir = Path(__file__).resolve().parent
        args = ["--from", str(parent_dir)]
        env = os.environ.copy()
        export_vals = "\n".join([f"export {var}={env[var]}" for var in CLAUDE_ENVVARS if var in env])
        shell_cmds = ["bash", "-c", f"cat >> ~/.bashrc << 'EOF'\n{export_vals}\nEOF"]
        super().__init__(args=args, shell_cmds=shell_cmds)

    def create(self):
        """Create a Claude provider."""
        self.openshell.provider_create(name=self.name)
