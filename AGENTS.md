# AI Helpers Marketplace

This repository serves as a collaborative marketplace for AI automation tools, plugins, and assistants designed to enhance productivity across multiple AI platforms. It provides a centralized location for sharing and discovering AI-powered development tools.

## Repository Purpose

The odh-ai-helpers repository hosts collections of:
- **Claude Code Plugins**: Custom commands, skills, agents that extend Claude Code's functionality
- **Cursor AI Commands**: Custom commands for Cursor AI integration
- **Gemini Gems**: Specialized AI assistants for various development tasks

This enables teams to automate repetitive tasks, integrate with development tools, and create specialized AI assistants tailored to specific workflows and needs.

## Supported AI Platforms

### Claude Code
Claude Code plugins extend Claude's functionality with custom commands for specific workflows. Plugins use a structured format with JSON metadata and Markdown command definitions.

**→ For detailed Claude Code development instructions, see [@claude-plugins/README.md](claude-plugins/README.md)**

### Cursor AI
Cursor commands provide custom AI functionality within the Cursor development environment. Commands are implemented as simple Markdown files with descriptive instructions.

**→ For detailed Cursor development instructions, see [@cursor/README.md](cursor/README.md)**

### Gemini Gems
Gemini Gems are specialized AI assistants created within Google's Gemini platform. Each Gem can be tailored with specific instructions and knowledge bases for particular tasks.

**→ For detailed Gemini Gems instructions, see [@gemini-gems/README.md](gemini-gems/README.md)**

## How to Create New Tools

### Development Workflow (All Platforms)

1. **Plan Your Tool**
   - Identify the specific task or workflow to automate
   - Choose the appropriate platform based on requirements
   - Review existing tools to avoid duplication

2. **Follow Platform Guidelines**
   - Read the platform-specific README for detailed instructions
   - Study existing examples in the respective directories
   - Follow naming and structure conventions

3. **Validate and Test**
   ```bash
   make lint      # Validate plugin structure
   make update    # Regenerate documentation
   ```

4. **Submit Contribution**
   - Test your tool thoroughly
   - Update relevant documentation
   - Submit a merge request with your changes

## Ethical Guidelines

**Critical Requirement**: Never reference real people by name in plugins, commands, or examples.

**Instead of naming people, describe qualities explicitly:**
- ✅ "Write commit messages that are direct, technically precise, and focused on rationale"
- ✅ "Explain using clear analogies, wonder, and accessible language for non-experts"
- ❌ "Write commits in the style of [person's name]"

This ensures consent, prevents misrepresentation, respects intellectual property, and maintains dignity.

## Getting Started

1. **Explore Existing Tools**: Browse [TOOLS.md](TOOLS.md) for available tools
2. **Choose Your Platform**: Review platform-specific READMEs for detailed guidance
3. **Study Examples**: Look at existing implementations for structure and patterns
4. **Start Contributing**: Follow the development workflow for your chosen platform
