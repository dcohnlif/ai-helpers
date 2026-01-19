# AI Helpers Marketplace

This repository serves as a collaborative marketplace for AI automation tools, plugins, and assistants designed to enhance productivity across multiple AI platforms. It provides a centralized location for sharing and discovering AI-powered development tools.

## Repository Purpose

The odh-ai-helpers repository hosts collections of four distinct tool types:
- **Skills**: Standardized capabilities using agentskills.io format, compatible with Claude Code and Cursor
- **Commands**: Atomic, executable actions for immediate functionality
- **Agents**: Specialized AI entities for complex, multi-step workflows and analysis
- **Gemini Gems**: Conversational AI assistants optimized for specific domains

This enables teams to automate repetitive tasks, integrate with development tools, and create specialized AI capabilities tailored to specific workflows and needs.

## Tool Types

### Skills
Standardized capabilities that work across multiple AI platforms using the agentskills.io specification. Skills provide reusable functionality with cross-platform compatibility.

**→ Located in [helpers/skills/](helpers/skills/) directory**

### Commands
Atomic, executable actions that provide immediate functionality. Commands are designed for quick, specific tasks and can be invoked directly by AI agents.

**→ Located in [helpers/commands/](helpers/commands/) directory**

### Agents
Specialized AI entities capable of complex reasoning and multi-step workflows. Agents maintain context and can execute sophisticated analysis within their domain of expertise.

**→ Located in [helpers/agents/](helpers/agents/) directory**

### Gemini Gems
Conversational AI assistants created within Google's Gemini platform. Each Gem is tailored with specific instructions and knowledge bases for particular domains or tasks.

**→ For detailed Gemini Gems instructions, see [Gemini Gems README](helpers/gems/README.md)**

## Platform Support

### Claude Code
- **Skills**: Available through marketplace plugin entries
- **Commands**: Available through marketplace plugin entries
- **Agents**: Available as sub-agents through marketplace plugin entries


### Cursor AI
- **Skills**: Compatible through agentskills.io format
- **Commands**: Can be adapted for Cursor command structure
- **Agents**: Can be used as specialized workflow guides

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
   make lint      # Validate tool structure
   make update    # Update settings and website data
   ```

4. **Submit Contribution**
   - Test your tool thoroughly
   - Update relevant documentation
   - Submit a merge request with your changes

## Tool Registry

The marketplace uses a centralized tool registry in `tools.json` to organize all available tools by their type and category. This provides a single source of truth for tool discovery and maintains a well-structured tool collection.

### Tool Registry Structure

All tools are defined in `tools.json` at the repository root with the following structure:

```json
{
  "tools": [
    {
      "name": "tool-name",
      "description": "Tool description",
      "type": "skill|command|agent|gem",
      "category": "category-name"
    }
  ],
  "categories": {
    "category-name": {
      "name": "Display Name",
      "description": "Category description"
    }
  }
}
```

### Available Categories

- **General**: Default category for general-purpose tools and utilities
- **AIPCC**: Tools specifically designed for AIPCC workflows and processes
- **vLLM**: Tools specifically designed for vLLM workflows and processes

### Adding a New Category

When you have multiple related tools that form a cohesive workflow or domain:

1. **Add category definition** to `tools.json`:
   ```json
   "categories": {
     "your-category": {
       "name": "Your Category Name",
       "description": "Clear description of the category's purpose and scope"
     }
   }
   ```

2. **Assign tools to the category** by setting their `category` field

3. **Update documentation**: Run `make update` to regenerate the website

### Category Guidelines

**When to create a new category:**
- You have 3+ related tools that share a common domain or workflow
- The tools serve a specific user group or use case
- The category provides clear value for tool discovery

**Category naming:**
- Use lowercase with hyphens for category keys (e.g., "data-science")
- Use clear, descriptive names for display (e.g., "Data Science")
- Write concise descriptions that explain the category's scope

### Automatic Management

The build system automatically handles tool registry maintenance:
- New tools are assigned to "general" if not explicitly categorized
- The registry is updated during `make update` to include new tools
- Manual categorizations are preserved across updates

This ensures all tools are properly registered and categorized without manual maintenance overhead.

## Ethical Guidelines

**Critical Requirement**: Never reference real people by name in plugins, commands, or examples.

**Instead of naming people, describe qualities explicitly:**
- ✅ "Write commit messages that are direct, technically precise, and focused on rationale"
- ✅ "Explain using clear analogies, wonder, and accessible language for non-experts"
- ❌ "Write commits in the style of [person's name]"

This ensures consent, prevents misrepresentation, respects intellectual property, and maintains dignity.

## Getting Started

1. **Explore Existing Tools**: Browse [tools.json](tools.json) for available tools or visit our [website](https://opendatahub-io.github.io/ai-helpers/)
2. **Choose Your Platform**: Review platform-specific READMEs for detailed guidance
3. **Study Examples**: Look at existing implementations for structure and patterns
4. **Start Contributing**: Follow the development workflow for your chosen platform
