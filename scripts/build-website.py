#!/usr/bin/env python3
"""
Build website data for ODH ai-helpers Github Pages
Extracts plugin and command information from the repository
"""

import json
import re
import yaml
from pathlib import Path
from typing import Dict, List


def parse_frontmatter(content: str) -> Dict[str, str]:
    """Extract frontmatter from markdown file"""
    frontmatter = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 2:
            fm_lines = parts[1].strip().split("\n")
            for line in fm_lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter[key.strip()] = value.strip()
    return frontmatter


def extract_synopsis(content: str) -> str:
    """Extract synopsis from command markdown"""
    match = re.search(r"## Synopsis\s*```\s*([^\n]+)", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def get_plugin_commands(
    plugin_path: Path, plugin_name: str = ""
) -> List[Dict[str, str]]:
    """Get all commands for a plugin"""
    commands = []
    commands_dir = plugin_path / "commands"

    if not commands_dir.exists():
        return commands

    for cmd_file in sorted(commands_dir.glob("*.md")):
        try:
            content = cmd_file.read_text()
            frontmatter = parse_frontmatter(content)
            synopsis = extract_synopsis(content)

            command_name = cmd_file.stem

            # Fix synopsis to use proper Claude Code format: /plugin:command
            if synopsis and plugin_name:
                # Replace the command part with the plugin:command format
                # E.g., "/sprint-summary <args>" becomes "/jira:sprint-summary <args>"
                synopsis = synopsis.replace(
                    f"/{command_name}", f"/{plugin_name}:{command_name}"
                )

            commands.append(
                {
                    "name": command_name,
                    "description": frontmatter.get("description", ""),
                    "synopsis": synopsis,
                    "argument_hint": frontmatter.get("argument-hint", ""),
                }
            )
        except Exception as e:
            print(f"Error processing {cmd_file}: {e}")

    return commands


def get_plugin_skills(plugin_path: Path) -> List[Dict[str, str]]:
    """Get all skills for a plugin"""
    skills = []
    skills_dir = plugin_path / "skills"

    if not skills_dir.exists():
        return skills

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue

        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue

        try:
            content = skill_file.read_text()
            frontmatter = parse_frontmatter(content)

            skill_name = skill_dir.name
            skills.append(
                {
                    "name": frontmatter.get("name", skill_name),
                    "id": skill_name,
                    "description": frontmatter.get("description", ""),
                }
            )
        except Exception as e:
            print(f"Error processing {skill_file}: {e}")

    return skills


def get_plugin_hooks(plugin_path: Path) -> List[Dict[str, str]]:
    """Get all hooks for a plugin"""
    hooks = []
    hooks_file = plugin_path / "hooks" / "hooks.json"

    if not hooks_file.exists():
        return hooks

    try:
        with open(hooks_file) as f:
            hooks_data = json.load(f)

        # Extract description and hook types
        description = hooks_data.get("description", "")
        hook_types = hooks_data.get("hooks", {})

        for hook_type, hook_configs in hook_types.items():
            hooks.append(
                {"name": hook_type, "description": description, "type": hook_type}
            )
    except Exception as e:
        print(f"Error processing {hooks_file}: {e}")

    return hooks


def get_plugin_agents(plugin_path: Path) -> List[Dict[str, str]]:
    """Get all agents for a plugin"""
    agents = []
    agents_dir = plugin_path / "agents"

    if not agents_dir.exists():
        return agents

    for agent_file in sorted(agents_dir.glob("*.md")):
        try:
            content = agent_file.read_text()
            frontmatter = parse_frontmatter(content)

            agent_name = agent_file.stem
            agents.append(
                {
                    "name": frontmatter.get("name", agent_name),
                    "id": agent_name,
                    "description": frontmatter.get("description", ""),
                    "tools": frontmatter.get("tools", ""),
                    "model": frontmatter.get("model", ""),
                }
            )
        except Exception as e:
            print(f"Error processing {agent_file}: {e}")

    return agents


def get_cursor_commands(cursor_path: Path) -> List[Dict[str, str]]:
    """Get all commands for cursor tools"""
    commands = []
    commands_dir = cursor_path / "commands"

    if not commands_dir.exists():
        return commands

    for cmd_file in sorted(commands_dir.glob("*.md")):
        try:
            content = cmd_file.read_text()
            frontmatter = parse_frontmatter(content)
            synopsis = extract_synopsis(content)

            command_name = cmd_file.stem
            # For cursor commands, use the full filename as the command name
            # e.g., 'git-commit-suggest' becomes '/git-commit-suggest'
            full_command_name = command_name

            # Extract display name for the command itself (last part after hyphen)
            parts = command_name.split("-", 1)
            if len(parts) > 1:
                display_name = parts[1]
            else:
                display_name = command_name

            # Fix synopsis for cursor commands to use proper format: /full-command-name
            if synopsis:
                # Replace the raw command with the full command name
                # E.g., "/sprint-summary <args>" becomes "/jira-sprint-summary <args>"
                cursor_synopsis = synopsis.replace(
                    f"/{display_name}", f"/{full_command_name}"
                )
                # Also handle cases where the synopsis might have the old :format
                cursor_synopsis = cursor_synopsis.replace(
                    f"/{command_name.split('-')[0]}:{display_name}",
                    f"/{full_command_name}",
                )
            else:
                cursor_synopsis = f"/{full_command_name}"

            commands.append(
                {
                    "name": display_name,
                    "full_command_name": full_command_name,
                    "description": frontmatter.get("description", ""),
                    "synopsis": cursor_synopsis,
                    "argument_hint": frontmatter.get("argument-hint", ""),
                }
            )
        except Exception as e:
            print(f"Error processing {cmd_file}: {e}")

    return commands


def get_gemini_gems(gems_dir: Path) -> List[Dict[str, any]]:
    """Get all Gemini Gems as individual tools for website display"""
    tools = []
    gems_file = gems_dir / "gems.yaml"

    if not gems_file.exists():
        return tools

    try:
        with open(gems_file, "r") as f:
            gems_data = yaml.safe_load(f)

        if not gems_data or "gems" not in gems_data:
            return tools

        for gem in gems_data["gems"]:
            gem_title = gem.get("title", "Untitled Gem")
            tools.append(
                {
                    "name": gem_title.lower().replace(" ", "-"),
                    "display_name": gem_title,
                    "description": gem.get("description", ""),
                    "link": gem.get("link", ""),
                    "commands": [],
                    "skills": [],
                    "hooks": [],
                    "agents": [],
                    "has_readme": False,
                }
            )
    except Exception as e:
        print(f"Error processing {gems_file}: {e}")

    return tools


def build_website_data():
    """Build complete website data structure"""
    # Get repository root (parent of scripts directory)
    base_path = Path(__file__).parent.parent
    marketplace_file = base_path / ".claude-plugin" / "marketplace.json"

    with open(marketplace_file) as f:
        marketplace = json.load(f)

    website_data = {
        "name": marketplace["name"],
        "owner": marketplace["owner"]["name"],
        "tools": {"claude_code": [], "cursor": [], "gemini": []},
    }

    # Process Claude Code plugins
    for plugin_info in marketplace["plugins"]:
        plugin_path = base_path / plugin_info["source"]

        # Get commands, skills, hooks, and agents
        commands = get_plugin_commands(plugin_path, plugin_info["name"])
        skills = get_plugin_skills(plugin_path)
        hooks = get_plugin_hooks(plugin_path)
        agents = get_plugin_agents(plugin_path)

        # Read README if exists
        readme_path = plugin_path / "README.md"

        plugin_data = {
            "name": plugin_info["name"],
            "description": plugin_info["description"],
            "commands": commands,
            "skills": skills,
            "hooks": hooks,
            "agents": agents,
            "has_readme": readme_path.exists(),
        }

        website_data["tools"]["claude_code"].append(plugin_data)

    # Process Cursor commands (each command as individual tool)
    cursor_path = base_path / "cursor"
    if cursor_path.exists():
        cursor_commands = get_cursor_commands(cursor_path)

        # Each cursor command becomes an individual tool entry
        for cmd in cursor_commands:
            # Get the full command name from the file (e.g., git-commit-suggest, jira-sprint-summary)
            cursor_tool_data = {
                "name": cmd[
                    "full_command_name"
                ],  # This will be added by get_cursor_commands
                "description": cmd["description"],
                "commands": [cmd],  # Single command per tool
                "skills": [],
                "hooks": [],
                "agents": [],
                "has_readme": (cursor_path / "README.md").exists(),
            }

            website_data["tools"]["cursor"].append(cursor_tool_data)

    # Process Gemini Gems
    gemini_gems_path = base_path / "gemini-gems"
    if gemini_gems_path.exists():
        gems = get_gemini_gems(gemini_gems_path)

        # Add each gem as an individual tool
        for gem_tool in gems:
            website_data["tools"]["gemini"].append(gem_tool)

    return website_data


if __name__ == "__main__":
    data = build_website_data()

    # Output as JSON (in docs directory at repo root)
    output_file = Path(__file__).parent.parent / "docs" / "data.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Website data written to {output_file}")

    # Calculate statistics
    claude_tools = data["tools"]["claude_code"]
    cursor_tools = data["tools"]["cursor"]
    gemini_tools = data["tools"]["gemini"]
    all_tools = claude_tools + cursor_tools + gemini_tools

    print(f"Total Claude Code plugins: {len(claude_tools)}")
    print(f"Total Cursor tools: {len(cursor_tools)}")
    print(f"Total Gemini Gems collections: {len(gemini_tools)}")
    print(f"Total tools: {len(all_tools)}")

    total_commands = sum(len(p["commands"]) for p in all_tools)
    print(f"Total commands: {total_commands}")

    total_skills = sum(len(p["skills"]) for p in all_tools)
    print(f"Total skills: {total_skills}")

    total_hooks = sum(len(p["hooks"]) for p in all_tools)
    print(f"Total hooks: {total_hooks}")

    total_agents = sum(len(p["agents"]) for p in all_tools)
    print(f"Total agents: {total_agents}")
