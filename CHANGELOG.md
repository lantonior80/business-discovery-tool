# Changelog

## 1.2.0 — 2026-11-18
- **Trimmed from 332 to 201 questions (355 facets).** 139 questions were retired:
  - 82 duplicates
  - 11 whose answers can be calculated from other answers
  - 9 line-by-line script questions that a call recording or written script answers
  - 35 not needed to map the funnels or judge business health (mostly educational-video planning)
  - 2 replaced by the new meeting questions

  Kept questions keep their IDs, and retired IDs are never reused.
- **No assumed meetings.** Module 6 now first asks how many meetings a buyer has before home tours and what type each one is (Q06.13–Q06.14). Meeting questions in Modules 6–10 are worded for any number or format of meetings, and Module 9 applies only when there is more than one meeting.
- **No assumed team size.** Q13.02 now asks how many agents the team has; the new Q13.17 then asks what each named agent owns, one agent at a time.
- **Back-end questions added (Q11.16–Q11.20):** offers, contracts and closings after tours; time to offer and to close; deals that fell apart and why; who handles a deal to closing; and listings.
- Removed leftovers from the private original: "four agents" and "California".
- The checker now reads the question count from `MANIFEST.json` instead of a fixed number, identically in Python and the JavaScript reference. The rule tests run against a frozen copy of the 1.1.0 questions in `tests/fixtures/`, and a new test checks that Python and JavaScript give byte-identical output on the shipped package.

## 1.1.0 — 2026-11-18
- **Two new modules, 63 new questions (332 total, 538 facets):**
  - **Module 17 — Business economics, client value and growth limits** (33 questions). Covers commission and closings, what the team keeps per deal, the cost to win and to serve a client, cash timing, repeat and referral business, the past-client database, offers after the first one, buyer-agreement terms, capacity and goals.
  - **Module 18 — Lead handling, team and proof operating numbers** (30 questions). Covers follow-up attempts, answer rates, booking availability, lead grading, reasons buyers don't move forward, agent and VA turnover, call review, onboarding, role standards, ads and reviews.
  - The 269 earlier questions and their 409 facets are unchanged.
- **Money basics.** Right after the opening, quick discovery asks 4 money questions (Q17.01–Q17.04). Like the opening, they don't count toward the budget. Quick discovery is now about 20–25 minutes.
- **Facts-only hand-off.** Nothing shown to the owner contains an evaluation, score, diagnosis or advice. The report's "preliminary diagnostic observations" section is now "contradictions and data gaps — facts only". The closing message tells the owner to send the file to the person who shared the tool, with a PDF copy available on request.
- The checker (Python and the JavaScript reference) now expects 332 questions. The question bank, rubric and MANIFEST hashes changed, so assessments made with 1.0.x must start from a fresh template.

## 1.0.2 — 2026-11-15
- Discovery now always opens by mapping how strangers find the business: lead sources → biggest source → what they're asked to do → where it lands (landing page, DMs…) → what's promised → where it goes first. Referrals get a short branch; a second source is mapped if named.
- The opening reuses existing questions (Q02.01–Q02.04, Q03.01–Q03.02) and doesn't count toward the 12-minute budget or six-answer fallback. Quick discovery is now about 15–20 minutes.
- Question bank, rubric, hashes and the checker are unchanged (269 questions, 409 facets). Only `DISCOVERY_GUIDE.md` and the Project instructions changed.

## Hub update — 2026-11-15 (tool files unchanged, still 1.0.1)
- One-line setup command instead of a paragraph.
- Setup now offers a choice: **A. Manual** (download and upload five files) or **B. Automated** (ChatGPT in a Work-mode Project does it; the person only signs in). New runbook: [AGENT_SETUP.md](AGENT_SETUP.md).
- Beginner "Start here" steps in the README.

## 1.0.1 — 2026-11-15
- Removed the Custom GPT route. Setup is the GitHub link only: paste the paragraph, follow the guided clicks in a ChatGPT or Claude Project.

## 1.0.0 — 2026-11-15
First public release.
- Five Project files: `DISCOVERY_GUIDE.md` (workflow, templates and validation in one file), `QUESTION_BANK.md`, `COVERAGE_RUBRIC.json`, `MANIFEST.json` and `validate_coverage.py`.
- Derived from the private D1 candidate. Six question texts and their rubric propositions were made team-neutral. All 269 IDs, priorities, 409 facets and qualifiers are unchanged. The built-in team profile was removed: the owner supplies every fact during the interview.
- New Python checker (`validate_coverage.py`), byte-identical to the JavaScript original across all 138 inherited tests. It runs in ChatGPT's and Claude's code tools.
- Paste-a-paragraph setup ([SETUP.md](SETUP.md)), a Custom GPT recipe (removed in 1.0.1) and a destination smoke test ([TESTING.md](TESTING.md)).
