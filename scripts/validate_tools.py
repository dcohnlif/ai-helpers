#!/usr/bin/env python3
"""
Validate tools.json structure and consistency

This script validates that:
1. Every category referenced by a tool exists in the categories section
2. Every category that exists is used by at least one tool
3. All tools have required fields
4. Tool types are valid

Usage:
    python3 scripts/validate_tools.py [tools.json]

Returns:
    0 on success
    1 on validation errors
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List

try:
    import yaml
except ImportError:
    yaml = None


VALID_TOOL_TYPES = {"skill", "command", "agent", "gem"}
REQUIRED_TOOL_FIELDS = {"name", "description", "type", "category"}
ALLOWED_TOOL_FIELDS = REQUIRED_TOOL_FIELDS  # Only required fields are allowed


def title_to_slug(title: str) -> str:
    """Convert gem title to slug format (lowercase, spaces/special chars to hyphens)"""
    return re.sub(r"[^a-zA-Z0-9]+", "-", title.lower()).strip("-")


def get_filesystem_tools(helpers_dir: Path) -> Dict[str, str]:
    """Extract all tool names from the filesystem with their types

    Returns:
        Dict mapping tool name to tool type
    """
    filesystem_tools = {}

    # Skills - directories in helpers/skills/
    skills_dir = helpers_dir / "skills"
    if skills_dir.exists() and skills_dir.is_dir():
        for item in skills_dir.iterdir():
            if item.is_dir():
                filesystem_tools[item.name] = "skill"

    # Commands - .md files in helpers/commands/
    commands_dir = helpers_dir / "commands"
    if commands_dir.exists() and commands_dir.is_dir():
        for item in commands_dir.iterdir():
            if item.is_file() and item.suffix == ".md":
                # Skip README.md files (case-insensitive)
                if item.name.lower() == "readme.md":
                    continue
                filesystem_tools[item.stem] = "command"

    # Agents - .md files in helpers/agents/
    agents_dir = helpers_dir / "agents"
    if agents_dir.exists() and agents_dir.is_dir():
        for item in agents_dir.iterdir():
            if item.is_file() and item.suffix == ".md":
                # Skip README.md files (case-insensitive)
                if item.name.lower() == "readme.md":
                    continue
                filesystem_tools[item.stem] = "agent"

    # Gems - titles from gems.yaml
    gems_file = helpers_dir / "gems" / "gems.yaml"
    if gems_file.exists() and gems_file.is_file():
        if yaml is None:
            # Warn when gems.yaml exists but PyYAML is not available
            print(
                f"Warning: Found gems.yaml but PyYAML is not installed. "
                f"Gem validation skipped. Install PyYAML (pip install PyYAML) "
                f"or remove {gems_file} to disable gem validation.",
                file=sys.stderr,
            )
        else:
            try:
                with open(gems_file, "r", encoding="utf-8") as f:
                    gems_data = yaml.safe_load(f)

                if gems_data and "gems" in gems_data:
                    for gem in gems_data["gems"]:
                        if "title" in gem:
                            tool_name = title_to_slug(gem["title"])
                            filesystem_tools[tool_name] = "gem"
            except (yaml.YAMLError, IOError) as e:
                print(
                    f"Warning: Could not parse gems.yaml ({gems_file}): {e}",
                    file=sys.stderr,
                )

    return filesystem_tools


def load_tools_json(path: Path) -> Dict:
    """Load and parse tools.json file"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {path} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {path}: {e}")
        sys.exit(1)


def validate_tool_structure(tool: Dict, index: int) -> List[str]:
    """Validate individual tool structure"""
    errors = []
    tool_name = tool.get("name", f"tool[{index}]")

    # Check required fields
    missing_fields = REQUIRED_TOOL_FIELDS - set(tool.keys())
    for field in missing_fields:
        errors.append(f"Tool '{tool_name}' is missing required field: {field}")

    # Check for disallowed fields
    disallowed_fields = set(tool.keys()) - ALLOWED_TOOL_FIELDS
    for field in sorted(disallowed_fields):
        errors.append(
            f"Tool '{tool_name}' has disallowed field: {field}. Only allowed fields: {', '.join(sorted(ALLOWED_TOOL_FIELDS))}"
        )

    # Check tool type is valid
    tool_type = tool.get("type")
    if tool_type and tool_type not in VALID_TOOL_TYPES:
        errors.append(
            f"Tool '{tool_name}' has invalid type '{tool_type}'. Valid types: {', '.join(sorted(VALID_TOOL_TYPES))}"
        )

    # Check required fields are strings and non-empty
    for field in REQUIRED_TOOL_FIELDS:
        value = tool.get(field)
        if value is not None:
            if not isinstance(value, str):
                errors.append(
                    f"Tool '{tool_name}' field '{field}' must be a string, got {type(value).__name__}"
                )
            elif not value.strip():
                errors.append(f"Tool '{tool_name}' has empty {field}")

    return errors


def validate_categories(tools: List[Dict], categories: Dict) -> List[str]:
    """Validate category consistency"""
    errors = []

    # Get referenced and defined categories
    referenced_categories = set()
    for i, tool in enumerate(tools):
        category = tool.get("category")
        if category:
            if not isinstance(category, str):
                tool_name = tool.get("name", f"tool[{i}]")
                errors.append(
                    f"Tool '{tool_name}' field 'category' must be a string, got {type(category).__name__}"
                )
            else:
                referenced_categories.add(category)

    defined_categories = set(categories.keys())

    # Check for referenced categories that don't exist
    missing_categories = referenced_categories - defined_categories
    for category in sorted(missing_categories):
        errors.append(
            f"Category '{category}' is referenced by tools but not defined in categories section"
        )

    # Check for defined categories that aren't used
    unused_categories = defined_categories - referenced_categories
    for category in sorted(unused_categories):
        errors.append(f"Category '{category}' is defined but not used by any tools")

    return errors


def validate_category_structure(categories: Dict) -> List[str]:
    """Validate category definitions"""
    errors = []

    for category_key, category_data in categories.items():
        if not isinstance(category_data, dict):
            errors.append(
                f"Category '{category_key}' must be an object, got {type(category_data).__name__}"
            )
            continue

        # Check required fields
        if "name" not in category_data:
            errors.append(f"Category '{category_key}' is missing required field: name")
        if "description" not in category_data:
            errors.append(
                f"Category '{category_key}' is missing required field: description"
            )

        # Check name field is string and non-empty
        name = category_data.get("name")
        if name is not None:
            if not isinstance(name, str):
                errors.append(
                    f"Category '{category_key}' field 'name' must be a string, got {type(name).__name__}"
                )
            elif not name.strip():
                errors.append(f"Category '{category_key}' has empty name")

        # Check description field is string and non-empty
        description = category_data.get("description")
        if description is not None:
            if not isinstance(description, str):
                errors.append(
                    f"Category '{category_key}' field 'description' must be a string, got {type(description).__name__}"
                )
            elif not description.strip():
                errors.append(f"Category '{category_key}' has empty description")

    return errors


def validate_tool_names_unique(tools: List[Dict]) -> List[str]:
    """Validate that tool names are unique"""
    errors = []
    seen_names = set()

    for tool in tools:
        name = tool.get("name")
        if name:
            if name in seen_names:
                errors.append(f"Duplicate tool name: '{name}'")
            else:
                seen_names.add(name)

    return errors


def validate_filesystem_tools_in_json(tools_data: Dict, helpers_dir: Path) -> List[str]:
    """Validate that all filesystem tools have entries in tools.json"""
    errors = []

    # Get tools from both sources
    filesystem_tools = get_filesystem_tools(helpers_dir)
    json_tools = {
        tool.get("name"): tool.get("type") for tool in tools_data.get("tools", [])
    }

    # Check for missing tools
    for tool_name, expected_type in filesystem_tools.items():
        if tool_name not in json_tools:
            errors.append(
                f"Tool '{tool_name}' (type: {expected_type}) found in filesystem but missing from tools.json"
            )
        elif json_tools[tool_name] != expected_type:
            errors.append(
                f"Tool '{tool_name}' has mismatched type: filesystem={expected_type}, tools.json={json_tools[tool_name]}"
            )

    return errors


def validate_tools_json(tools_data: Dict, helpers_dir: Path = None) -> List[str]:
    """Run all validations on tools.json data"""
    errors = []

    # Check top-level structure
    if "tools" not in tools_data:
        errors.append("Missing required 'tools' field")
        return errors

    if "categories" not in tools_data:
        errors.append("Missing required 'categories' field")
        return errors

    tools = tools_data.get("tools", [])
    categories = tools_data.get("categories", {})

    if not isinstance(tools, list):
        errors.append("'tools' field must be an array")
        return errors

    if not isinstance(categories, dict):
        errors.append("'categories' field must be an object")
        return errors

    # Validate individual tools
    for i, tool in enumerate(tools):
        if not isinstance(tool, dict):
            errors.append(
                f"Tool at index {i} must be an object, got {type(tool).__name__}"
            )
            continue
        errors.extend(validate_tool_structure(tool, i))

    # Validate unique tool names
    errors.extend(validate_tool_names_unique(tools))

    # Validate categories
    errors.extend(validate_category_structure(categories))
    errors.extend(validate_categories(tools, categories))

    # Validate filesystem tools are in tools.json (if helpers_dir is provided)
    if helpers_dir and helpers_dir.exists():
        errors.extend(validate_filesystem_tools_in_json(tools_data, helpers_dir))

    return errors


def main():
    """Main validation function"""
    # Determine tools.json path
    if len(sys.argv) > 1:
        tools_json_path = Path(sys.argv[1])
    else:
        # Default to tools.json in the current directory
        tools_json_path = Path("tools.json")

    # Determine helpers directory path
    helpers_dir = tools_json_path.parent / "helpers"

    # Load tools.json
    tools_data = load_tools_json(tools_json_path)

    # Validate tools.json
    errors = validate_tools_json(tools_data, helpers_dir)

    # Report results
    if errors:
        print("tools.json validation errors found:")
        for error in errors:
            print(f"  ✗ {error}")
        print(f"\n{len(errors)} error(s) found.")
        sys.exit(1)
    else:
        print("✓ All tools.json validations passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
