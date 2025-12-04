"""
Custom claudelint rules for AIPCC AI helpers
"""

import subprocess
from typing import List

try:
    from src.rule import Rule, RuleViolation, Severity
    from src.context import RepositoryContext
except ImportError:
    # Fallback for when running as a custom rule
    from claudelint import Rule, RuleViolation, Severity, RepositoryContext


class PluginsDocUpToDateRule(Rule):
    """Check that TOOLS.md, docs/data.json, and images/claude-settings.json are up-to-date by running 'make update'"""

    @property
    def rule_id(self) -> str:
        return "plugins-doc-up-to-date"

    @property
    def description(self) -> str:
        return "TOOLS.md, docs/data.json, and images/claude-settings.json must be up-to-date with plugin metadata. Run 'make update' to regenerate."

    def default_severity(self) -> Severity:
        return Severity.ERROR

    def check(self, context: RepositoryContext) -> List[RuleViolation]:
        violations = []

        # Only check marketplace repos
        if not context.has_marketplace():
            return violations

        tools_md_path = context.root_path / "TOOLS.md"
        data_json_path = context.root_path / "docs" / "data.json"
        claude_settings_path = context.root_path / "images" / "claude-settings.json"

        if not tools_md_path.exists():
            return violations

        # Check if generate_tools_docs.py script exists
        script_path = context.root_path / "scripts" / "generate_tools_docs.py"
        if not script_path.exists():
            return violations

        try:
            # Read current content of files to check
            original_tools_md = tools_md_path.read_text()
            original_data_json = (
                data_json_path.read_text() if data_json_path.exists() else None
            )
            original_claude_settings = (
                claude_settings_path.read_text()
                if claude_settings_path.exists()
                else None
            )

            # Run the docs generation script
            result = subprocess.run(
                ["python3", str(script_path)],
                cwd=str(context.root_path),
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                violations.append(
                    self.violation(
                        f"'make update' failed: {result.stderr}",
                        file_path=tools_md_path,
                    )
                )
                return violations

            # Also run build-website.py if it exists
            website_script_path = context.root_path / "scripts" / "build-website.py"
            if website_script_path.exists():
                result = subprocess.run(
                    ["python3", str(website_script_path)],
                    cwd=str(context.root_path),
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode != 0:
                    violations.append(
                        self.violation(
                            f"build-website.py failed: {result.stderr}",
                            file_path=data_json_path
                            if data_json_path.exists()
                            else tools_md_path,
                        )
                    )
                    return violations

            # Also run update_claude_settings.py if it exists
            claude_settings_script_path = (
                context.root_path / "scripts" / "update_claude_settings.py"
            )
            if claude_settings_script_path.exists():
                result = subprocess.run(
                    ["python3", str(claude_settings_script_path)],
                    cwd=str(context.root_path),
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode != 0:
                    violations.append(
                        self.violation(
                            f"update_claude_settings.py failed: {result.stderr}",
                            file_path=claude_settings_path
                            if claude_settings_path.exists()
                            else tools_md_path,
                        )
                    )
                    return violations

            # Check if TOOLS.md changed
            generated_tools_md = tools_md_path.read_text()
            if original_tools_md != generated_tools_md:
                # Restore original content
                tools_md_path.write_text(original_tools_md)

                violations.append(
                    self.violation(
                        "TOOLS.md is out of sync with plugin metadata. Run 'make update' to update.",
                        file_path=tools_md_path,
                    )
                )

            # Check if docs/data.json changed
            if data_json_path.exists():
                generated_data_json = data_json_path.read_text()
                if original_data_json != generated_data_json:
                    # Restore original content
                    if original_data_json is not None:
                        data_json_path.write_text(original_data_json)

                    violations.append(
                        self.violation(
                            "docs/data.json is out of sync with plugin metadata. Run 'make update' to update.",
                            file_path=data_json_path,
                        )
                    )

            # Check if images/claude-settings.json changed
            if claude_settings_path.exists():
                generated_claude_settings = claude_settings_path.read_text()
                if original_claude_settings != generated_claude_settings:
                    # Restore original content
                    if original_claude_settings is not None:
                        claude_settings_path.write_text(original_claude_settings)

                    violations.append(
                        self.violation(
                            "images/claude-settings.json is out of sync with plugin metadata. Run 'make update' to update.",
                            file_path=claude_settings_path,
                        )
                    )

        except subprocess.TimeoutExpired:
            violations.append(
                self.violation("'make update' timed out", file_path=tools_md_path)
            )
        except Exception as e:
            violations.append(
                self.violation(
                    f"Error checking files up-to-date status: {e}",
                    file_path=tools_md_path,
                )
            )

        return violations


class MarketplacePluginsUpToDateRule(Rule):
    """Check that .claude-plugin/marketplace.json includes all available plugins"""

    @property
    def rule_id(self) -> str:
        return "marketplace-plugins-up-to-date"

    @property
    def description(self) -> str:
        return ".claude-plugin/marketplace.json must include all available plugins"

    def default_severity(self) -> Severity:
        return Severity.ERROR

    def check(self, context: RepositoryContext) -> List[RuleViolation]:
        violations = []

        # Only check repos with Claude plugins
        marketplace_path = context.root_path / ".claude-plugin" / "marketplace.json"
        if not marketplace_path.exists():
            return violations

        plugins_dir = context.root_path / "claude-plugins"
        if not plugins_dir.exists():
            return violations

        try:
            import json

            # Read marketplace.json
            with open(marketplace_path, "r") as f:
                marketplace_data = json.load(f)

            if "plugins" not in marketplace_data:
                violations.append(
                    self.violation(
                        "marketplace.json is missing 'plugins' field",
                        file_path=marketplace_path,
                    )
                )
                return violations

            # Get available plugin directories
            available_plugins = []
            for plugin_dir in plugins_dir.iterdir():
                if plugin_dir.is_dir():
                    available_plugins.append(plugin_dir.name)

            # Get plugins listed in marketplace.json
            marketplace_plugins = {}
            for plugin in marketplace_data["plugins"]:
                name = plugin.get("name")
                source = plugin.get("source")
                if name:
                    marketplace_plugins[name] = source

            # Check for missing plugins
            missing_plugins = set(available_plugins) - set(marketplace_plugins.keys())
            if missing_plugins:
                violations.append(
                    self.violation(
                        f"marketplace.json is missing plugins: {', '.join(sorted(missing_plugins))}",
                        file_path=marketplace_path,
                    )
                )

            # Check source paths are correct
            for plugin_name, source_path in marketplace_plugins.items():
                if plugin_name in available_plugins:
                    expected_source = f"./claude-plugins/{plugin_name}"
                    if source_path != expected_source:
                        violations.append(
                            self.violation(
                                f"Plugin '{plugin_name}' source path should be '{expected_source}', got '{source_path}'",
                                file_path=marketplace_path,
                            )
                        )

        except json.JSONDecodeError as e:
            violations.append(
                self.violation(
                    f"Invalid JSON in marketplace.json: {e}", file_path=marketplace_path
                )
            )
        except Exception as e:
            violations.append(
                self.violation(
                    f"Error checking marketplace.json: {e}", file_path=marketplace_path
                )
            )

        return violations
