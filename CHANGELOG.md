# Changelog

## 1.0.0 — 2026-11-15
First public release.
- Five Project files: `DISCOVERY_GUIDE.md` (workflow, templates and validation in one file), `QUESTION_BANK.md`, `COVERAGE_RUBRIC.json`, `MANIFEST.json` and `validate_coverage.py`.
- Derived from the private D1 candidate. Six question texts and their rubric propositions were made team-neutral. All 269 IDs, priorities, 409 facets and qualifiers are unchanged. The built-in team profile was removed: the owner supplies every fact during the interview.
- New Python checker (`validate_coverage.py`), byte-identical to the JavaScript original across all 138 inherited tests. It runs in ChatGPT's and Claude's code tools.
- Paste-a-paragraph setup ([SETUP.md](SETUP.md)), Custom GPT recipe ([GPT_SETUP.md](GPT_SETUP.md)) and a destination smoke test ([TESTING.md](TESTING.md)).
