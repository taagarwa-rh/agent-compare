from pathlib import Path

from agent_compare.openshell import OpenShell


class CustomProvider:
    """Base class for custom providers."""

    name: str

    def __init__(self, args: list[str] = None, shell_cmds: list[str] = None, policy: Path = None):
        """Initialize."""
        self.openshell = OpenShell()
        self.args = args
        self.shell_cmds = shell_cmds
        self.policy = policy

    def create(self):
        """Implement in child classes."""
        pass
