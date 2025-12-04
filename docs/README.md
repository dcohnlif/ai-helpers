# AI Helpers Website

This directory contains the Github Pages website for the ODH ai-helpers project.

## Structure

- `index.html` - Main website with plugin browser
- `data.json` - Plugin and command metadata (generated)
- `.nojekyll` - Tells Github Pages not to use Jekyll processing

## Building

The website data is generated from the repository structure:

```bash
# From repository root
python3 scripts/build-website.py
```

This extracts information from:
- `.claude-plugin/marketplace.json` - Plugin registry
- `claude-plugins/*/commands/*.md` - Command definitions
- `claude-plugins/*/skills/*/SKILL.md` - Skill definitions
- `claude-plugins/*/.claude-plugin/plugin.json` - Plugin metadata

## Local Development

To test the website locally:

```bash
cd docs
python3 -m http.server 8000
# Visit http://localhost:8000
```

## Deployment

The website is automatically deployed via Github Pages from the `docs/` directory.

The site will be available at: `https://opendatahub-io.github.io/ai-helpers/`

## Updating

When plugins or commands are added/modified:

1. Run `python3 scripts/build-website.py` to regenerate `data.json`
2. Commit both `data.json` and any changes
3. Push to trigger Github Pages rebuild

Alternatively, set up a Github workflow to automatically rebuild on changes.
