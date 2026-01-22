#!/usr/bin/env python3
"""
Update Claude Code marketplace by scanning tools from tools.json configuration.

This script loads the centralized tools.json file and generates:
- marketplace.json file with plugin catalog information
- claude-settings.json file with basic configuration
"""

import json
import sys
from pathlib import Path
from typing import Dict, List


def load_tools_config(tools_path: Path) -> Dict:
    """Load tools configuration from tools.json."""

    if not tools_path.exists():
        print(f"Error: Tools configuration not found: {tools_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(tools_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error: Could not read tools configuration: {e}", file=sys.stderr)
        sys.exit(1)


def get_tool_source_path(tool: Dict) -> str:
    """Generate source path for a tool based on its type."""

    # Validate required keys exist and are strings
    tool_type = tool.get("type")
    tool_name = tool.get("name")

    if not isinstance(tool_type, str) or not tool_type:
        print(f"Warning: Tool missing or invalid 'type' key: {tool}", file=sys.stderr)
        return ""

    if not isinstance(tool_name, str) or not tool_name:
        print(f"Warning: Tool missing or invalid 'name' key: {tool}", file=sys.stderr)
        return ""

    if tool_type == "skill":
        return f"./helpers/skills/{tool_name}"
    elif tool_type == "command":
        return f"./helpers/commands/{tool_name}.md"
    elif tool_type == "agent":
        return f"./helpers/agents/{tool_name}.md"
    elif tool_type == "gem":
        # For gems, we don't have a local source file, they're external
        return ""
    else:
        print(
            f"Warning: Unknown tool type '{tool_type}' for tool '{tool_name}'",
            file=sys.stderr,
        )
        return ""


def load_external_plugins(config_path: Path) -> List[Dict]:
    """Load external plugin definitions from config file.

    External plugins are specified with their source (github, git URL, etc.)
    and are included directly in the marketplace without cloning.
    """
    if not config_path.exists():
        return []

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not read external plugins config: {e}", file=sys.stderr)
        return []

    external_plugins = []
    for plugin in config.get("plugins", []):
        # Validate required fields
        if "name" not in plugin:
            print(
                f"Warning: Skipping external plugin missing 'name': {plugin}",
                file=sys.stderr,
            )
            continue
        if "source" not in plugin:
            print(
                f"Warning: Skipping external plugin '{plugin.get('name')}' missing 'source'",
                file=sys.stderr,
            )
            continue

        external_plugins.append(
            {
                "name": plugin["name"],
                "description": plugin.get("description", f"{plugin['name']} plugin"),
                "source": plugin["source"],
            }
        )

    return external_plugins


def generate_claude_settings(tools_config: Dict) -> Dict:
    """Generate Claude Code settings configuration."""

    # Base configuration
    settings = {
        "extraKnownMarketplaces": {
            "odh-ai-helpers": {
                "source": {"source": "directory", "path": "/opt/ai-helpers"}
            }
        },
        "enabledPlugins": {},
    }

    # Enable the single plugin containing all helpers
    settings["enabledPlugins"]["odh-ai-helpers@odh-ai-helpers"] = True

    return settings


def generate_marketplace_json(tools_config: Dict, external_plugins: List[Dict]) -> Dict:
    """Generate marketplace.json configuration."""

    # Base marketplace structure
    marketplace = {
        "name": "odh-ai-helpers",
        "owner": {"name": "ODH"},
        "plugins": [],
    }

    # Add external plugins first
    marketplace["plugins"].extend(external_plugins)

    # Add single plugin entry for all helpers
    marketplace["plugins"].append(
        {
            "name": "odh-ai-helpers",
            "source": "./helpers",
            "description": "AI automation tools, plugins, and assistants for enhanced productivity",
            "strict": False,
        }
    )

    return marketplace


def write_settings_file(settings_path: Path, settings: Dict) -> None:
    """Write the claude-settings.json file."""

    # Ensure the directory exists
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    # Write with proper formatting
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")  # Add final newline


def main():
    """Main entry point."""

    # Determine repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    tools_path = repo_root / "tools.json"
    settings_path = repo_root / "images" / "claude" / "claude-settings.json"
    marketplace_path = repo_root / ".claude-plugin" / "marketplace.json"
    external_sources_path = repo_root / "claude-external-plugin-sources.json"

    print("Loading tools configuration...")
    tools_config = load_tools_config(tools_path)

    tools = tools_config.get("tools")
    if not isinstance(tools, list):
        print("Error: tools.json missing required 'tools' array", file=sys.stderr)
        sys.exit(1)

    # Count tools by type
    tool_counts = {}
    for tool in tools:
        tool_type = tool.get("type")
        if not isinstance(tool_type, str) or not tool_type:
            print(
                f"Warning: Skipping tool with missing or invalid 'type' key: {tool}",
                file=sys.stderr,
            )
            continue
        tool_counts[tool_type] = tool_counts.get(tool_type, 0) + 1

    print("Found tools:")
    for tool_type, count in sorted(tool_counts.items()):
        tools_of_type = [
            t.get("name", "unknown")
            for t in tools
            if t.get("type") == tool_type and isinstance(t.get("name"), str)
        ]
        print(f"  {tool_type}: {count} ({', '.join(tools_of_type)})")

    # Load external plugins
    external_plugins = load_external_plugins(external_sources_path)
    if external_plugins:
        ext_names = [
            plugin.get("name", "unknown")
            for plugin in external_plugins
            if isinstance(plugin.get("name"), str)
        ]
        print(f"Found external plugins: {', '.join(ext_names)}")

    print("Generating Claude settings...")
    settings = generate_claude_settings(tools_config)

    print(f"Writing {settings_path}...")
    write_settings_file(settings_path, settings)

    print("Generating marketplace configuration...")
    marketplace = generate_marketplace_json(tools_config, external_plugins)

    print(f"Writing {marketplace_path}...")
    write_settings_file(marketplace_path, marketplace)

    print("✓ Claude settings and marketplace updated successfully!")


if __name__ == "__main__":
    main()
