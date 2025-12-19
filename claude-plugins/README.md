# Claude Code Plugin Development Guide

This directory contains Claude Code plugins for the AI helpers marketplace.

## Prerequisites

**Read the official Claude Code documentation first:**
- **Plugin Reference**: https://code.claude.com/docs/en/plugins-reference.md
- **Skills Guide**: https://code.claude.com/docs/en/skills.md
- **Sub-Agents Guide**: https://code.claude.com/docs/en/sub-agents.md

## Quick Start

1. **Choose existing plugin or create new one**: git/, utils/, python-packaging/, or new directory
2. **Choose component type**: Commands, Skills, or Agents
3. **Follow plugin structure** (see Plugin Categories section)
4. **Validate and test**: `make lint && make update`

## Adding New Content

### Adding to Existing Plugins
```bash
# Commands
claude-plugins/{plugin}/commands/your-command.md

# Skills
claude-plugins/{plugin}/skills/your-skill/SKILL.md

# Agents
claude-plugins/{plugin}/agents/your-agent.md
```

### Creating New Plugin
```bash
# Create structure
mkdir -p claude-plugins/your-plugin/{.claude-plugin,commands,skills,agents}

# Required: plugin.json with name, description, version, author
# See existing plugins for examples
```

## Development Workflow

1. **Create your plugin file** following official Claude documentation formats
2. **Validate**: `make lint`
3. **Update docs**: `make update`
4. **Test locally**: Install plugin and test functionality

## Python Script Dependencies

When creating Python scripts that require external dependencies (beyond the standard library), use `uv` with PEP 723 inline script metadata. This allows scripts to manage their own dependencies.

**Format**: Add a header to the top of your Python script:

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "python-gitlab>=4.0.0",
# ]
# ///

# Your script code here
```

**When to use**:
- Scripts that import non-standard-library packages
- Helper scripts that need specific package versions
- Tools that should be easy to run without manual virtualenv setup

**Important**:
- All scripts MUST have a proper shebang (`#!/usr/bin/env python3` or `#!/usr/bin/env -S uv run --script`)
- All scripts MUST be executable (`chmod +x script.py`)
- Plugin documentation should instruct Claude to run scripts as `./scripts/script_name.py`, not `python script_name.py`
- Do NOT document tool requirements (Python, uv, etc.) in skill/command prerequisites, the shebang handles this automatically. Claude will figure out any missing prerequisites from the error message if needed.

## Plugin Categories

**Existing**: git/ (commands), hello-world/ (reference), python-packaging/ (skills+agents), utils/ (misc)

**Create new plugin when**: 3+ related components, shared domain/theme, needs supporting files

## Including External Plugins

To include plugins from other repositories without copying them locally, add them to `claude-external-plugin-sources.json` in the repository root:

```json
{
  "version": "1.0",
  "plugins": [
    {
      "name": "my-plugin",
      "description": "Description of the plugin",
      "source": {
        "source": "url",
        "url": "https://github.com/org/plugin-repo.git"
      }
    }
  ]
}
```

Optional fields: `ref` (branch/tag), `path` (subdirectory within repo)

> **Note:** Use HTTPS URLs rather than the `github` source type, as the latter requires SSH keys which may not be available in container environments.

Run `make update` after adding external plugins to regenerate the marketplace.

## Reference Examples

- **Commands**: `hello-world/commands/echo.md`
- **Skills**: `python-packaging/skills/complexity/SKILL.md`
- **Agents**: `python-packaging/agents/investigator.md`
