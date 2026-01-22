#!/usr/bin/env python3
"""
Build website data for ODH ai-helpers Github Pages
Loads tool information from centralized tools.json configuration
"""

import json
import sys
import yaml
from pathlib import Path
from typing import Dict


def load_tools_config(tools_path: Path) -> Dict:
    """Load tools configuration from tools.json."""

    if not tools_path.exists():
        print(f"Error: Tools configuration not found: {tools_path}")
        sys.exit(1)

    try:
        with open(tools_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error: Could not read tools configuration: {e}")
        sys.exit(1)


def get_tool_file_path(tool: Dict, base_path: Path) -> str:
    """Generate file path for a tool based on its type."""

    tool_type = tool["type"]
    tool_name = tool["name"]

    if tool_type == "skill":
        skill_file = base_path / "helpers" / "skills" / tool_name / "SKILL.md"
        if skill_file.exists():
            return f"helpers/skills/{tool_name}/SKILL.md"
        else:
            print(f"Warning: Skill file not found: {skill_file}")
            return f"helpers/skills/{tool_name}/SKILL.md"
    elif tool_type == "command":
        return f"helpers/commands/{tool_name}.md"
    elif tool_type == "agent":
        return f"helpers/agents/{tool_name}.md"
    elif tool_type == "gem":
        # Gems are external, no local file path
        return ""
    else:
        print(f"Warning: Unknown tool type '{tool_type}' for tool '{tool_name}'")
        return ""


def get_tool_metadata(tool: Dict, base_path: Path) -> Dict:
    """Get additional metadata for a tool by reading its file."""

    metadata = {
        "name": tool["name"],
        "description": tool["description"],
        "category": tool["category"],
        "file_path": get_tool_file_path(tool, base_path),
    }

    tool_type = tool["type"]

    if tool_type == "skill":
        # Read additional skill metadata from SKILL.md
        skill_file = base_path / "helpers" / "skills" / tool["name"] / "SKILL.md"
        if skill_file.exists():
            try:
                content = skill_file.read_text()

                # Parse YAML frontmatter
                if content.startswith("---\n"):
                    end_marker = content.find("\n---\n", 4)
                    if end_marker != -1:
                        frontmatter_content = content[4:end_marker]
                        skill_data = yaml.safe_load(frontmatter_content)

                        metadata.update(
                            {
                                "id": tool["name"],
                                "allowed_tools": skill_data.get("allowed-tools", ""),
                            }
                        )
            except Exception as e:
                print(f"Warning: Could not read skill metadata from {skill_file}: {e}")

        # Add default fields for skills
        if "id" not in metadata:
            metadata["id"] = tool["name"]
        if "allowed_tools" not in metadata:
            metadata["allowed_tools"] = ""

    elif tool_type == "command":
        # Read command metadata from frontmatter
        cmd_file = base_path / "helpers" / "commands" / f"{tool['name']}.md"
        if cmd_file.exists():
            try:
                content = cmd_file.read_text()
                frontmatter = {}

                # Parse frontmatter - simple key: value parser
                if content.startswith("---\n"):
                    end_marker = content.find("\n---\n", 4)
                    if end_marker != -1:
                        frontmatter_content = content[4:end_marker]
                        for line in frontmatter_content.strip().split("\n"):
                            if ":" in line:
                                key, value = line.split(":", 1)
                                frontmatter[key.strip()] = value.strip()

                # Extract synopsis
                import re

                match = re.search(
                    r"## Synopsis\s*```[^\n]*\n([^\n]+)", content, re.MULTILINE
                )

                # Only add synopsis to metadata if we found a non-empty match
                metadata_updates = {
                    "argument_hint": frontmatter.get("argument-hint", "")
                }
                if match:
                    synopsis = match.group(1).strip()
                    if synopsis:  # Only add if non-empty
                        metadata_updates["synopsis"] = synopsis

                metadata.update(metadata_updates)
            except Exception as e:
                print(f"Warning: Could not read command metadata from {cmd_file}: {e}")

        # Add default fields for commands
        if "synopsis" not in metadata:
            metadata["synopsis"] = f"/{tool['name']}"
        if "argument_hint" not in metadata:
            metadata["argument_hint"] = ""

    elif tool_type == "agent":
        # Read agent metadata from frontmatter
        agent_file = base_path / "helpers" / "agents" / f"{tool['name']}.md"
        if agent_file.exists():
            try:
                content = agent_file.read_text()

                # Parse YAML frontmatter
                if content.startswith("---\n"):
                    end_marker = content.find("\n---\n", 4)
                    if end_marker != -1:
                        frontmatter_content = content[4:end_marker]
                        agent_data = yaml.safe_load(frontmatter_content)

                        metadata.update(
                            {
                                "id": tool["name"],
                                "tools": agent_data.get("tools", ""),
                                "model": agent_data.get("model", ""),
                            }
                        )
            except Exception as e:
                print(f"Warning: Could not read agent metadata from {agent_file}: {e}")

        # Add default fields for agents
        if "id" not in metadata:
            metadata["id"] = tool["name"]
        if "tools" not in metadata:
            metadata["tools"] = ""
        if "model" not in metadata:
            metadata["model"] = ""

    elif tool_type == "gem":
        # Look up link from gems.yaml by matching tool name
        link = ""

        gemini_gems_path = base_path / "helpers" / "gems" / "gems.yaml"
        if gemini_gems_path.exists():
            try:
                with open(gemini_gems_path) as f:
                    gems_data = yaml.safe_load(f)

                # Find matching gem by converting gem title to kebab-case
                def title_to_kebab_case(title):
                    """Convert gem title to kebab-case for matching with tool names"""
                    import re

                    # Replace spaces and special characters with hyphens
                    kebab = re.sub(r"[^\w\s-]", "", title.lower())
                    kebab = re.sub(r"[-\s]+", "-", kebab)
                    return kebab.strip("-")

                tool_name = tool["name"]

                for gem in gems_data.get("gems", []):
                    gem_title = gem.get("title", "")
                    if gem_title and title_to_kebab_case(gem_title) == tool_name:
                        link = gem.get("link", "")
                        break
            except Exception as e:
                print(f"Warning: Could not read gemini gems data: {e}")

        metadata.update(
            {
                "link": link,
            }
        )

    return metadata


def build_website_data():
    """Build complete website data structure"""
    # Get repository root (parent of scripts directory)
    base_path = Path(__file__).parent.parent
    tools_path = base_path / "tools.json"

    # Load tools configuration
    tools_config = load_tools_config(tools_path)

    website_data = {
        "name": "odh-ai-helpers",
        "owner": "ODH",
        "categories": {"categories": tools_config["categories"]},
        "tools": {"gemini": [], "skills": [], "commands": [], "agents": []},
    }

    # Process all tools
    for tool in tools_config["tools"]:
        # Validate tool dictionary has expected keys
        if not isinstance(tool, dict):
            print(f"Warning: Malformed tool entry (not a dict): {tool}")
            continue

        required_keys = ["name", "type", "description", "category"]
        missing_keys = [key for key in required_keys if key not in tool]
        if missing_keys:
            print(f"Warning: Tool missing required keys {missing_keys}: {tool}")
            continue

        tool_metadata = get_tool_metadata(tool, base_path)
        tool_type = tool["type"]

        if tool_type == "skill":
            website_data["tools"]["skills"].append(tool_metadata)
        elif tool_type == "command":
            website_data["tools"]["commands"].append(tool_metadata)
        elif tool_type == "agent":
            website_data["tools"]["agents"].append(tool_metadata)
        elif tool_type == "gem":
            website_data["tools"]["gemini"].append(tool_metadata)

    return website_data


if __name__ == "__main__":
    data = build_website_data()

    # Output as JSON (in docs directory at repo root)
    output_file = Path(__file__).parent.parent / "docs" / "data.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Website data written to {output_file}")

    # Calculate statistics for new tool structure
    skills_tools = data["tools"]["skills"]
    commands_tools = data["tools"]["commands"]
    agents_tools = data["tools"]["agents"]
    gemini_tools = data["tools"]["gemini"]
    all_tools = skills_tools + commands_tools + agents_tools + gemini_tools

    print(f"Total Skills: {len(skills_tools)}")
    print(f"Total Commands: {len(commands_tools)}")
    print(f"Total Agents: {len(agents_tools)}")
    print(f"Total Gemini Gems: {len(gemini_tools)}")
    print(f"Total tools: {len(all_tools)}")
