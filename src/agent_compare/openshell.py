import os
import re
import subprocess
from pathlib import Path
from typing import Union


def strip_ansi(text: str) -> str:
    """Strip ANSI encoding from text."""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


class OpenShell:
    """Wrapper for the openshell CLI tool."""

    def __init__(self, executable: str = "openshell"):
        """Initialize."""
        self.executable = executable

    def exec(self, cmd: list[str]) -> subprocess.CompletedProcess[str]:
        """Execute a command."""
        env = os.environ.copy()
        out = subprocess.run(cmd, env=env, capture_output=True, text=True)
        try:
            out.check_returncode()
        except subprocess.CalledProcessError as e:
            raise Exception(f"Command {e.cmd} failed with exit code {e.returncode}: {e.stderr}")
        return out

    def provider_list(self) -> list[str]:
        """List all available providers."""
        cmd = [
            self.executable,
            "provider",
            "list",
            "--names",
        ]
        out = self.exec(cmd)
        return out.stdout.splitlines()

    def provider_create(self, name: str, credentials: Union[list[str], dict[str, str]] = None, args: list[str] = None):
        """Create a provider."""
        # Check if provider already exists
        providers = self.provider_list()
        if name in providers:
            raise ValueError(f"Provider '{name}' already exists")

        # Build command
        creds = []
        if isinstance(credentials, dict):
            for k, v in credentials.items():
                creds.extend(["--credential", f"{k}={v}"])
        elif isinstance(credentials, list):
            for k in credentials:
                creds.extend(["--credential", k])
        cmd = (
            [
                self.executable,
                "provider",
                "create",
                "--name",
                name,
                "--type",
                "generic",
            ]
            + (creds if len(creds) > 0 else ["--credential", "NULL_KEY=0"])
            + (args or [])
        )
        print(cmd)

        # Execute command
        self.exec(cmd)

    def sandbox_list(self) -> list[str]:
        """List all available sandboxes."""
        cmd = [
            self.executable,
            "sandbox",
            "list",
            "--names",
        ]
        out = self.exec(cmd)
        return out.stdout.splitlines()

    def sandbox_create(
        self,
        provider: str,
        context: Path,
        policy: Path = None,
        args: list[str] = None,
        shell_cmds: list[str] = None,
    ) -> str:
        """Start up a sandbox."""
        # Build command
        if not context.is_dir():
            raise ValueError("Passed context is not a directory")
        local_path = context.resolve().as_posix()
        sandbox_path = f"/sandbox/{context.resolve().name}"

        ## Openshell args
        cmd = [
            self.executable,
            "sandbox",
            "create",
            "--provider",
            provider,
            "--upload",
            f"{local_path}:{sandbox_path}",
        ]
        cmd += ["--policy", str(policy)] if policy else []
        cmd += args or []

        ## Shell commands
        cmd += ["--"]
        cmd += shell_cmds or ["echo", "Ready"]

        # Run command
        out = self.exec(cmd)
        output = strip_ansi(out.stdout)

        # Parse sandbox name - pattern "Created sandbox: {name}"
        name = re.search(r"Created sandbox: (.+)", output).group(1).strip()
        return name

    def sandbox_delete(self, name: str):
        """Delete the specified sandbox."""
        if name not in self.sandbox_list():
            raise ValueError(f"Sandbox '{name}' does not exist.")

        cmd = [
            self.executable,
            "sandbox",
            "delete",
            name,
        ]
        self.exec(cmd)


if __name__ == "__main__":
    openshell = OpenShell()
    openshell.startup()
