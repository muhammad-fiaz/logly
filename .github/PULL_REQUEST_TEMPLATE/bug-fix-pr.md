---
name: Bug Fix Pull Request
about: Submit a pull request for fixing a bug
title: '[BUGFIX] '
labels: bugfix, triage
---

## Description

A clear and concise description of the bug fix.

## Related Issue URL

Fixes # (issue number)

Link: https://github.com/muhammad-fiaz/logly/issues/ISSUE_NUMBER

## Root Cause

**What was the root cause of the bug?**

Explain what caused the bug and why it occurred.

## Solution

**How was the bug fixed?**

Describe the technical solution and implementation details.

## Testing

**How was this fix tested?**

- [ ] Unit tests added/updated
- [ ] Integration tests
- [ ] Manual testing steps
- [ ] Test results

## Logly Version

What version of Logly was this tested against? (e.g., 0.1.4)

## Code Quality Checklist

Please confirm the following:

- [ ] `cargo fmt` has been run
- [ ] `mypy` passes with no errors
- [ ] `pylint` and `clippy` pass with no warnings
- [ ] `cargo test` and `pytest` pass
- [ ] `uv run ruff format` has been applied
- [ ] All new functions/classes have docstrings
- [ ] No unnecessary changes included

## AI Usage Disclosure

Please select one:

- [ ] I have used AI tools (GitHub Copilot, ChatGPT, etc.) to assist with this implementation
- [ ] No AI tools were used in this implementation

## Reviewers

@mention the person or team responsible for reviewing this PR

## Breaking Changes (if any)

Does this fix introduce any breaking changes?

If yes, describe them and provide migration guidance:
- Breaking change 1
- Migration steps...

## Additional Notes

Any additional information or context reviewers should be aware of:

- Performance impact
- Security considerations
- Future improvements
- Related PRs

---

**IMPORTANT**: Please review the [CONTRIBUTING.md](../CONTRIBUTING.md) file for detailed contributing guidelines.
