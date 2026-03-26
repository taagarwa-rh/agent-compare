from pathlib import Path

import click

from agent_compare.playground import CUSTOM_PROVIDERS, CUSTOM_PROVIDERS_MAP, Playground

persist_path = Path.cwd() / ".agent-compare.json"
pg = Playground(persist_path=persist_path)


@click.group()
def cli():
    """Agent compare command line tools."""
    pass


## CUSTOM PROVIDERS ##


@cli.group()
def provider():
    """Manage agent providers."""
    pass


@provider.command("list")
def provider_list():
    """List the available custom providers."""
    title = "Available Custom Providers"
    print()
    print(title)
    print("=" * len(title))
    for p in CUSTOM_PROVIDERS:
        print(f"{p.name}")


@provider.command("create")
@click.argument("provider_name")
def provider_create(provider_name: str):
    """Create one of the custom providers."""
    # Check that the provider name is valid
    if provider_name not in CUSTOM_PROVIDERS_MAP:
        raise ValueError(f"Custom provider {provider_name} not found. Please choose from {list(CUSTOM_PROVIDERS_MAP.keys())}.")

    # Create the provider
    p = CUSTOM_PROVIDERS_MAP[provider_name]
    try:
        p.create()
        print(f"Successfully created provider '{provider_name}'")
    except Exception as e:
        if "already exists" in str(e):
            print(f"Provider '{provider_name}' already exists")
        else:
            raise e


## PLAYGROUND ##


@cli.group()
def playground():
    """Manage agent playground."""
    pass


def list_running_sandboxes():
    """List all available running sandboxes."""
    if len(pg.sandboxes) == 0:
        print("No sandboxes running. Start a new playground by running `agent-compare playground start`.")
        return

    provider_sandbox = [(s["provider"], s["name"]) for s in pg.sandboxes.values()]
    title = "Running Sandboxes"
    print()
    print(title)
    print("=" * len(title))
    print("\n".join([f"{p}: {n}" for p, n in provider_sandbox]))
    print()
    print("=" * len(title))
    print("Connect to running sandboxes using the following commands:")
    print()
    for provider, sandbox in provider_sandbox:
        print(f"{provider}:")
        print(f"    openshell sandbox connect {sandbox}")
        print()


@playground.command("start")
@click.option("--providers", type=str, help="List of providers to start, as a comma separated list.", required=True)
@click.option("--context", type=Path, help="Path to the context directory.", required=True)
def playground_start(providers: str, context: Path):
    """Start the playground."""
    # Raise an error if sandboxes are already running
    if len(pg.sandboxes) > 0:
        print("ERROR: You have running sandboxes. Please close them before starting new ones using `agent-compare playground stop`.")
        list_running_sandboxes()
        return

    # Start the playground
    _providers = providers.split(",")
    pg.start(providers=_providers, context=context)

    # Print user message
    provider_sandbox = [(s["provider"], s["name"]) for s in pg.sandboxes.values()]
    title = "Sandboxes started successfully"
    print()
    print(title)
    print("=" * len(title))
    print("\n".join([f"{p}: {n}" for p, n in provider_sandbox]))
    print()
    print("=" * len(title))
    print("Connect to running sandboxes using the following commands:")
    print()
    for provider, sandbox in provider_sandbox:
        print(f"{provider}:")
        print(f"    openshell sandbox connect {sandbox}")

    # Persist the sandbox configs
    pg.persist()


@playground.command("list")
def playground_list():
    """List the sandboxes."""
    list_running_sandboxes()


@playground.command("stop")
def playground_stop():
    """Stop the playground."""
    print("Stopping playground...")
    # Stop the playground
    pg.stop()
    print("Playground stopped successfully")
    pg.persist()


if __name__ == "__main__":
    cli()
