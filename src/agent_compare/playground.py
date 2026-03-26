import json
from pathlib import Path

from agent_compare.custom_providers import CustomClaudeProvider, CustomGeminiProvider, CustomProvider
from agent_compare.openshell import OpenShell

CUSTOM_PROVIDERS: list[CustomProvider] = [CustomClaudeProvider(), CustomGeminiProvider()]
CUSTOM_PROVIDERS_MAP: dict[str, CustomProvider] = {p.name: p for p in CUSTOM_PROVIDERS}


class Playground:
    """Playground object, a collection of sandboxes."""

    def __init__(self, persist_path: Path):
        """Initialize."""
        # Initialize the openshell and sandboxes
        self.openshell = OpenShell()
        self.sandboxes = {}

        # Save the persist path and load sandboxes
        self.persist_path = persist_path
        self.load()

    def load(self):
        """Load the playground from the persist path."""
        # Create the persist path if it does not exist
        if not self.persist_path.exists():
            with open(self.persist_path, "w") as f:
                json.dump({}, f)
        # Load the sandboxes from the persist path
        with open(self.persist_path, "r") as f:
            self.sandboxes: dict[str, dict[str, str]] = json.load(f)
        # Check if the sandboxes are still active
        active_sandboxes = self.openshell.sandbox_list()
        loaded_sandboxes = list(self.sandboxes.keys())
        for sandbox in loaded_sandboxes:
            if sandbox not in active_sandboxes:
                self.sandboxes.pop(sandbox)
        # Update the persist file
        self.persist()

    def persist(self):
        """Persist the playground to the persist path."""
        # Persist the sandboxes to the persist path
        with open(self.persist_path, "w") as f:
            json.dump(self.sandboxes, f)

    def start(self, providers: list[str], context: Path) -> list[str]:
        """Start the sandboxes."""
        available_providers = self.openshell.provider_list()
        if any(p not in available_providers for p in providers):
            invalid_providers = [p for p in providers if p not in available_providers]
            raise ValueError(f"Invalid providers: {invalid_providers}")

        # Create a sandbox for each provider
        for p in providers:
            shell_cmds = None
            policy = None
            args = None
            if p in CUSTOM_PROVIDERS_MAP:
                custom_provider = CUSTOM_PROVIDERS_MAP[p]
                args = custom_provider.args
                policy = custom_provider.policy
                shell_cmds = custom_provider.shell_cmds
            try:
                name = self.openshell.sandbox_create(provider=p, context=context, policy=policy, args=args, shell_cmds=shell_cmds)
            except Exception as e:
                raise ValueError(f"Failed to create sandbox for provider '{p}': {e}")
            self.sandboxes[name] = {"name": name, "provider": p, "context": context.resolve().as_posix()}

        # Return the names of the created sandboxes
        created_sandboxes = list(self.sandboxes.keys())
        return created_sandboxes

    def stop(self):
        """Stop the sandboxes."""
        sandboxes = list(self.sandboxes.keys())
        for name in sandboxes:
            self.openshell.sandbox_delete(name)
            self.sandboxes.pop(name)
