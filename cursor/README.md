# Cursor AI Helpers

This directory contains custom commands and functionalities specifically designed for Cursor AI integration.

## Installing Cursor Commands 

Cursor is able to find the various commands defined in this repo by
making it available inside your `~/.cursor/commands` directory.
 
```
$ mkdir -p ~/.cursor/commands
$ git clone git@github.com:opendatahub-io/ai-helpers.git
$ cd ai-helpers
$ ln -sf $(pwd)/cursor/commands/* ~/.cursor/commands/
```

## Creating New Commands

### Prerequisites

**Before starting, read the official Cursor commands documentation:**
- https://cursor.com/docs/agent/chat/commands

This provides the foundational knowledge for command creation in Cursor.

### Quick Start

1. **Create command file**:
   ```bash
   touch cursor/commands/your-command.md
   ```

2. **Write command content**:
   - Use plain Markdown format
   - Describe the command's purpose and implementation
   - Include examples and expected behavior

3. **Update the Marketplace**:
   ```bash
   make update
   ```

### File Naming

- Use descriptive, hyphenated names: `review-code.md`, `create-pr.md`
- Avoid special characters except hyphens
- Keep names concise but clear

### Best Practices

1. **Clear Purpose**: Each command should have one clear responsibility
2. **Detailed Instructions**: Provide comprehensive implementation guidance
3. **Examples**: Include practical usage examples
4. **Context**: Explain when and why to use the command

### Development Workflow

1. **Plan**: Identify the specific task the command will handle
2. **Create**: Write the command file with clear instructions
3. **Test**: Use the command in Cursor to verify it works as expected
4. **Iterate**: Refine based on actual usage and feedback
