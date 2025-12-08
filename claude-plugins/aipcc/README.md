# AIPCC Plugin

Tools specifically designed for AIPCC workflows and processes.

## Commands

### commit-suggest

Generate AIPCC-formatted commit messages or summarize existing commits.

```bash
/aipcc:commit-suggest       # Analyze staged changes
/aipcc:commit-suggest [N]   # Analyze last N commits (1-100)
```

**Features:**
- Generates 3 AIPCC-formatted commit message suggestions (Recommended, Standard, Minimal)
- Supports analysis of staged changes or existing commits
- Interactive selection and automatic commit execution with sign-off
- Maintains AIPCC project format requirements

**Use cases:**
- Create AIPCC-formatted commit messages
- Improve or rewrite existing commits to meet project standards
- Generate squash messages for MR merges

## AIPCC Format Requirements

All commits must follow the AIPCC project format:

```
AIPCC-XXX: Short description

Longer explanation of what the commit does, written in at least one
complete sentence explaining the purpose and impact of the change.

[Optional: Fixes AIPCC-XXX]

[Optional: Co-Authored-By: [AI_NAME] ([AI_MODEL])]

Signed-off-by: Your Name <your.email@example.com>
```

### Required Elements
- **Title**: Must start with "AIPCC-XXX:" followed by a short description
- **Body**: Must explain what the commit does in at least one complete sentence
- **Sign-off**: All commits must include `Signed-off-by` line

### Optional Elements
- **Jira Integration**: Include "Fixes AIPCC-XXX" to automatically close tickets
- **Co-authors**: `Co-Authored-By: Name <email@example.com>`
- **AI Attribution**: `Co-Authored-By: [AI_NAME] ([AI_MODEL])`

## Examples

```bash
# Generate message for staged files
git add src/auth.ts src/middleware.ts
/aipcc:commit-suggest

# Rewrite last commit message
/aipcc:commit-suggest 1

# Summarize last 5 commits for squash
/aipcc:commit-suggest 5
```
