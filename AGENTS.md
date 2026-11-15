# Business Discovery Tool — notes for AI agents

This repository is the **hub** for a chat-based discovery questionnaire. It holds no business facts.

## If a person asked you to set the tool up
Follow [SETUP.md](SETUP.md) step by step. They are not technical: one step at a time, plain English, and they do the clicks.

## If you are running the discovery here (Claude Code, Codex, or any agent with file access)
Read `project-files/DISCOVERY_GUIDE.md` in full and follow it. The question bank, rubric, manifest and checker sit next to it in `project-files/`. Run the checker with `python project-files/validate_coverage.py <assessment.json>`. Save reports to a folder the person chooses, outside this repository. Never commit a real person's answers here.

## If you are changing the tool itself
- **Frozen files:** `project-files/QUESTION_BANK.md` and `project-files/COVERAGE_RUBRIC.json` are bound by hash in `MANIFEST.json`. Never edit them to fit answers. A real change means a new release with recomputed hashes (`python tools/build_release.py --rehash`) and a full test run.
- **The two checkers must agree:** `validate_coverage.py` must give byte-identical results to `reference-js/validate-coverage.mjs`. Run `python -m unittest discover -s tests`; the parity test runs whenever Node is installed.
- **Instruction limit:** `instructions/PROJECT_INSTRUCTIONS.txt` must stay under 8,000 characters, since that's the ChatGPT and Claude limit. A test enforces it.
- **No private data:** no names, team facts, client data or personal paths, in files or in git history.
