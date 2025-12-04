#!/usr/bin/env python3
"""
Generate tool documentation by scanning all tools in the repository.

This script scans the tools directories, reads tool metadata and command files,
and generates a markdown documentation section listing all available tools and commands.
"""

import json
import re
import sys
import yaml
from pathlib import Path
from typing import Dict, List


class ToolInfo:
    """Information about a tool (Claude Code plugin or Cursor command)."""

    def __init__(self, name: str, description: str, tool_type: str = "claude_code"):
        self.name = name
        self.description = description
        self.tool_type = tool_type  # 'claude_code' or 'cursor'
        self.commands = []
        self.skills = []
        self.agents = []

    def add_command(self, command_name: str, description: str, argument_hint: str = ""):
        """Add a command to this tool."""
        self.commands.append(
            {
                "name": command_name,
                "description": description,
                "argument_hint": argument_hint,
            }
        )

    def add_skill(self, skill_name: str, description: str):
        """Add a skill to this tool."""
        self.skills.append({"name": skill_name, "description": description})

    def add_agent(
        self, agent_name: str, description: str, tools: str = "", model: str = ""
    ):
        """Add an agent to this tool."""
        self.agents.append(
            {
                "name": agent_name,
                "description": description,
                "tools": tools,
                "model": model,
            }
        )


def parse_frontmatter(content: str) -> Dict[str, str]:
    """Parse YAML frontmatter from a markdown file."""
    frontmatter = {}

    # Match frontmatter between --- markers
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if match:
        frontmatter_text = match.group(1)

        # Parse simple YAML key-value pairs
        for line in frontmatter_text.split("\n"):
            line = line.strip()
            if ":" in line:
                key, value = line.split(":", 1)
                frontmatter[key.strip()] = value.strip()

    return frontmatter


def get_cursor_tools(cursor_dir: Path) -> List[ToolInfo]:
    """Extract cursor tool information from cursor directory."""
    tools = []

    # Check if cursor directory exists
    if not cursor_dir.exists():
        return tools

    commands_dir = cursor_dir / "commands"
    if not commands_dir.exists():
        return tools

    # Group commands by tool name (extract from filename pattern)
    tool_commands = {}

    for command_file in sorted(commands_dir.glob("*.md")):
        with open(command_file, "r") as f:
            content = f.read()

        frontmatter = parse_frontmatter(content)
        command_name = command_file.stem

        # Extract tool name from command name (e.g., 'git-commit-suggest' -> 'git')
        tool_name = command_name.split("-")[0]

        if tool_name not in tool_commands:
            tool_commands[tool_name] = []

        tool_commands[tool_name].append(
            {
                "name": command_name.replace(f"{tool_name}-", ""),
                "description": frontmatter.get("description", ""),
                "argument_hint": frontmatter.get("argument-hint", ""),
            }
        )

    # Create ToolInfo objects for each tool
    for tool_name, commands in tool_commands.items():
        tool_info = ToolInfo(
            name=tool_name,
            description=f"{tool_name.title()} workflow automation for Cursor AI integration",
            tool_type="cursor",
        )

        for cmd in commands:
            tool_info.add_command(
                command_name=cmd["name"],
                description=cmd["description"],
                argument_hint=cmd["argument_hint"],
            )

        tools.append(tool_info)

    return tools


def get_gemini_gems(gems_dir: Path) -> List[ToolInfo]:
    """Extract Gemini Gems information from gems directory."""
    tools = []

    # Check if gems directory exists
    if not gems_dir.exists():
        return tools

    gems_file = gems_dir / "gems.yaml"
    if not gems_file.exists():
        return tools

    try:
        with open(gems_file, "r") as f:
            gems_data = yaml.safe_load(f)

        if not gems_data or "gems" not in gems_data:
            return tools

        # Create individual tool for each gem
        for gem in gems_data["gems"]:
            gem_title = gem.get("title", "Untitled Gem")
            gem_tool = ToolInfo(
                name=gem_title.lower().replace(" ", "-"),
                description=gem.get("description", ""),
                tool_type="gemini",
            )

            # Add the gem link as a single "command"
            gem_tool.add_command(
                command_name="open",
                description=f"Open {gem_title}",
                argument_hint=gem.get("link", ""),
            )

            tools.append(gem_tool)

    except Exception as e:
        print(f"Error processing {gems_file}: {e}")

    return tools


def get_tool_info(tool_dir: Path) -> ToolInfo:
    """Extract tool information from plugin.json and command files."""

    # Read tool metadata
    tool_json_path = tool_dir / ".claude-plugin" / "plugin.json"
    if not tool_json_path.exists():
        return None

    with open(tool_json_path, "r") as f:
        tool_data = json.load(f)

    tool_info = ToolInfo(
        name=tool_data.get("name", tool_dir.name),
        description=tool_data.get("description", ""),
        tool_type="claude_code",
    )

    # Scan commands
    commands_dir = tool_dir / "commands"
    if commands_dir.exists():
        command_files = sorted(commands_dir.glob("*.md"))

        for command_file in command_files:
            with open(command_file, "r") as f:
                content = f.read()

            frontmatter = parse_frontmatter(content)
            command_name = command_file.stem

            tool_info.add_command(
                command_name=command_name,
                description=frontmatter.get("description", ""),
                argument_hint=frontmatter.get("argument-hint", ""),
            )

    # Scan skills
    skills_dir = tool_dir / "skills"
    if skills_dir.exists():
        skill_dirs = sorted([d for d in skills_dir.iterdir() if d.is_dir()])

        for skill_dir in skill_dirs:
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                with open(skill_file, "r") as f:
                    content = f.read()

                frontmatter = parse_frontmatter(content)
                skill_name = frontmatter.get("name", skill_dir.name)

                tool_info.add_skill(
                    skill_name=skill_name,
                    description=frontmatter.get("description", ""),
                )

    # Scan agents
    agents_dir = tool_dir / "agents"
    if agents_dir.exists():
        agent_files = sorted(agents_dir.glob("*.md"))

        for agent_file in agent_files:
            with open(agent_file, "r") as f:
                content = f.read()

            frontmatter = parse_frontmatter(content)
            agent_name = frontmatter.get("name", agent_file.stem)

            tool_info.add_agent(
                agent_name=agent_name,
                description=frontmatter.get("description", ""),
                tools=frontmatter.get("tools", ""),
                model=frontmatter.get("model", ""),
            )

    return tool_info


def generate_tools_docs(repo_root: Path) -> str:
    """Generate markdown documentation for all tools (Claude Code tools and Cursor tools)."""

    # Collect Claude Code tools
    claude_tools = []
    tools_dir = repo_root / "claude-plugins"
    if tools_dir.exists():
        for tool_dir in sorted(tools_dir.iterdir()):
            if not tool_dir.is_dir():
                continue

            tool_info = get_tool_info(tool_dir)
            if tool_info and (
                tool_info.commands or tool_info.skills or tool_info.agents
            ):
                claude_tools.append(tool_info)

    # Collect Cursor tools
    cursor_tools = []
    cursor_dir = repo_root / "cursor"
    if cursor_dir.exists():
        cursor_tools = get_cursor_tools(cursor_dir)

    # Collect Gemini Gems
    gemini_tools = []
    gems_dir = repo_root / "gemini-gems"
    if gems_dir.exists():
        gemini_tools = get_gemini_gems(gems_dir)

    # Combine all tools
    all_tools = claude_tools + cursor_tools + gemini_tools

    # Generate markdown
    lines = []
    lines.append("# Available Tools")
    lines.append("")
    lines.append(
        "This document lists all available Claude Code tools, Cursor tools, and Gemini Gems in the ODH ai-helpers repository."
    )
    lines.append("")

    # Separate tools by type
    claude_code_tools = [t for t in all_tools if t.tool_type == "claude_code"]
    cursor_tools = [t for t in all_tools if t.tool_type == "cursor"]
    gemini_tools = [t for t in all_tools if t.tool_type == "gemini"]

    # Generate table of contents
    if claude_code_tools:
        lines.append("## Claude Code Tools")
        lines.append("")
        for tool in claude_code_tools:
            tool_title = tool.name.replace("-", " ").title()
            anchor = tool_title.lower().replace(" ", "-") + "-claude-code-tool"
            lines.append(f"- [{tool_title}](#{anchor})")
        lines.append("")

    if cursor_tools:
        lines.append("## Cursor Tools")
        lines.append("")
        for tool in cursor_tools:
            tool_title = tool.name.replace("-", " ").title()
            anchor = tool_title.lower().replace(" ", "-") + "-cursor-tool"
            lines.append(f"- [{tool_title}](#{anchor})")
        lines.append("")

    if gemini_tools:
        lines.append("## Gemini Gems")
        lines.append("")
        for tool in gemini_tools:
            tool_title = tool.name.replace("-", " ").title()
            anchor = tool_title.lower().replace(" ", "-") + "-gemini-gems"
            lines.append(f"- [{tool_title}](#{anchor})")
        lines.append("")

    # Generate Claude Code plugins section
    if claude_code_tools:
        lines.append("## Claude Code Tools")
        lines.append("")
        for tool in claude_code_tools:
            lines.append(f"### {tool.name.replace('-', ' ').title()} Claude Code Tool")
            lines.append("")

            if tool.description:
                lines.append(tool.description)
                lines.append("")

            # Commands list
            if tool.commands:
                lines.append("**Commands:**")
                for cmd in tool.commands:
                    cmd_signature = f"`/{tool.name}:{cmd['name']}`"
                    if cmd["argument_hint"]:
                        cmd_signature += f" `{cmd['argument_hint']}`"
                    lines.append(f"- **{cmd_signature}** - {cmd['description']}")
                lines.append("")

            # Skills list
            if tool.skills:
                lines.append("**Skills:**")
                for skill in tool.skills:
                    lines.append(f"- **{skill['name']}** - {skill['description']}")
                lines.append("")

            # Agents list
            if tool.agents:
                lines.append("**Agents:**")
                for agent in tool.agents:
                    agent_desc = f"- **{agent['name']}** - {agent['description']}"
                    if agent["tools"]:
                        agent_desc += f" (Tools: {agent['tools']})"
                    if agent["model"]:
                        agent_desc += f" (Model: {agent['model']})"
                    lines.append(agent_desc)
                lines.append("")

            # Link to tool README if it exists
            readme_path = repo_root / "claude-plugins" / tool.name / "README.md"
            if readme_path.exists():
                lines.append(
                    f"See [claude-plugins/{tool.name}/README.md](claude-plugins/{tool.name}/README.md) for detailed documentation."
                )
                lines.append("")

    # Generate Cursor tools section
    if cursor_tools:
        lines.append("## Cursor Tools")
        lines.append("")
        for tool in cursor_tools:
            lines.append(f"### {tool.name.replace('-', ' ').title()} Cursor Tool")
            lines.append("")

            if tool.description:
                lines.append(tool.description)
                lines.append("")

            # Commands list
            if tool.commands:
                lines.append("**Commands:**")
                for cmd in tool.commands:
                    # For cursor tools, use the full command name as it appears in the filename
                    # For example: jira-sprint-summary.md -> /jira-sprint-summary
                    cmd_signature = f"`/{tool.name}-{cmd['name']}`"
                    if cmd["argument_hint"]:
                        cmd_signature += f" `{cmd['argument_hint']}`"
                    lines.append(f"- **{cmd_signature}** - {cmd['description']}")
                lines.append("")

            # Link to cursor README if it exists
            cursor_readme_path = repo_root / "cursor" / "README.md"
            if cursor_readme_path.exists():
                lines.append(
                    "See [cursor/README.md](cursor/README.md) for installation and usage instructions."
                )
                lines.append("")

    # Generate Gemini Gems section
    if gemini_tools:
        lines.append("## Gemini Gems")
        lines.append("")

        # Add general description
        lines.append(
            "Curated collection of Gemini Gems - specialized AI assistants for various development tasks."
        )
        lines.append("")

        for tool in gemini_tools:
            gem_title = tool.name.replace("-", " ").title()
            lines.append(f"### {gem_title}")
            lines.append("")

            if tool.description:
                lines.append(tool.description)
                lines.append("")

            # Add gem link
            if tool.commands:
                gem_link = tool.commands[0][
                    "argument_hint"
                ]  # Link is stored in argument_hint
                if gem_link:
                    lines.append(f"**🔗 [Open {gem_title}]({gem_link})**")
                    lines.append("")

        # Link to gemini-gems README if it exists
        gems_readme_path = repo_root / "gemini-gems" / "README.md"
        if gems_readme_path.exists():
            lines.append(
                "See [gemini-gems/README.md](gemini-gems/README.md) for more information about Gemini Gems and how to contribute."
            )
            lines.append("")

    return "\n".join(lines)


def write_tools_file(tools_path: Path, tools_content: str) -> None:
    """Write the TOOLS.md file with tool documentation."""

    with open(tools_path, "w") as f:
        f.write(tools_content)


def main():
    """Main entry point."""

    # Determine repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    tools_path = repo_root / "TOOLS.md"

    # Check that at least one tool directory exists
    tools_dir = repo_root / "claude-plugins"
    cursor_dir = repo_root / "cursor"
    gems_dir = repo_root / "gemini-gems"

    if not tools_dir.exists() and not cursor_dir.exists() and not gems_dir.exists():
        print(
            f"Error: No tool directories found. Expected {tools_dir}, {cursor_dir}, or {gems_dir}",
            file=sys.stderr,
        )
        sys.exit(1)

    print("Scanning tools...")
    tools_docs = generate_tools_docs(repo_root)

    print("Writing TOOLS.md...")
    write_tools_file(tools_path, tools_docs)

    print("✓ Tool documentation updated successfully in TOOLS.md!")


if __name__ == "__main__":
    main()
