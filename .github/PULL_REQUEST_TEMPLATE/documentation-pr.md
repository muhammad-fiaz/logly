---
name: Documentation Pull Request
about: Submit a pull request for documentation updates
title: '[DOCS] '
labels: documentation, triage
---

## Documentation Type

What type of documentation is being updated?

- [ ] API Reference
- [ ] Quick Start Guide
- [ ] User Guide
- [ ] Examples/Cookbook
- [ ] README
- [ ] Code Comments/Docstrings
- [ ] Changelog
- [ ] Other

## Documentation Location

Where is the documentation located?

e.g., `docs/api-reference/logging.md`, `README.md`, `examples/basic-console.md`

## Changes Made

**What documentation changes were made?**

- What was added, updated, or corrected?
- What sections were affected?
- What examples were added or modified?

## Reason for Changes

**Why was this documentation update needed?**

- What was unclear, incorrect, or missing?
- What user feedback prompted this change?
- What new features need documentation?
- What bugs were documented?

## Related Issue URL (if applicable)

Link to any related GitHub issue

https://github.com/muhammad-fiaz/logly/issues/ISSUE_NUMBER

## Validation

**How was the documentation validated?**

- [ ] Documentation builds successfully (`mkdocs build`)
- [ ] Links are working
- [ ] Examples are correct and runnable
- [ ] Screenshots/images are updated
- [ ] Cross-references are accurate

## Documentation Checklist

Please confirm the following:

- [ ] Documentation builds without warnings or errors
- [ ] All links are working and accurate
- [ ] Code examples are correct and runnable
- [ ] Screenshots/images are updated if needed
- [ ] Table of contents and navigation are correct
- [ ] Spelling and grammar are correct

## Code Quality Checklist (if code changes included)

If this PR includes code changes, please confirm:

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

## Documentation Preview

If applicable, provide links to preview the documentation changes:

- Local build URL
- Netlify/GitHub Pages preview
- Screenshots of changes

## Additional Notes

Any additional information or context reviewers should be aware of:

- Impact on user experience
- Related documentation updates needed
- Translation requirements
- Accessibility considerations

---

**IMPORTANT**: Please review the [CONTRIBUTING.md](../CONTRIBUTING.md) file for detailed contributing guidelines.
