# Changelog

## Hub update — 2026-11-15 (tool files unchanged, still 1.0.1)
- One-line setup command instead of a paragraph.
- Setup now offers a choice: **A. Manual** (download and upload five files) or **B. Automated** (ChatGPT Agent mode does it; the person only signs in). New runbook: [AGENT_SETUP.md](AGENT_SETUP.md).
- Beginner "Start here" steps in the README.

## 1.0.1 — 2026-11-15
- Removed the Custom GPT route. Setup is the GitHub link only: paste the paragraph, follow the guided clicks in a ChatGPT or Claude Project.

## 1.0.0 — 2026-11-15
First public release.
- Five Project files: `DISCOVERY_GUIDE.md` (workflow, templates and validation in one file), `QUESTION_BANK.md`, `COVERAGE_RUBRIC.json`, `MANIFEST.json` and `validate_coverage.py`.
- Derived from the private D1 candidate. Six question texts and their rubric propositions were made team-neutral. All 269 IDs, priorities, 409 facets and qualifiers are unchanged. The built-in team profile was removed: the owner supplies every fact during the interview.
- New Python checker (`validate_coverage.py`), byte-identical to the JavaScript original across all 138 inherited tests. It runs in ChatGPT's and Claude's code tools.
- Paste-a-paragraph setup ([SETUP.md](SETUP.md)), a Custom GPT recipe (removed in 1.0.1) and a destination smoke test ([TESTING.md](TESTING.md)).
