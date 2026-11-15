# Business Discovery Tool

**A friendly AI interviewer that maps how a real-estate team turns leads into buyers, one short question at a time, and saves the answers as a shareable report.**

It works inside a **ChatGPT Project**, a **Claude Project** or a **Custom GPT**. The owner just chats with it, by typing or voice. Behind the scenes it tracks 269 discovery questions, never asks the same thing twice, stops after about 12 minutes, and hands back one report file that can be picked up again later.

---

## Start here — paste this paragraph

Open **ChatGPT** or **Claude**, start a chat (inside a Project if you have one), and paste:

> You're setting up the "Business Discovery Tool" for me. I am NOT technical, so explain each step in plain English, give me one step at a time, and wait for me to say "done" before moving on. Open this setup guide and follow it exactly: https://raw.githubusercontent.com/lantonior80/business-discovery-tool/main/SETUP.md. If you can't open links, tell me and I'll open https://github.com/lantonior80/business-discovery-tool myself. Don't start the questionnaire until setup is finished.

The assistant then walks you through about five clicks: make a Project, download five files, add them, paste the instructions, and start.

**Even easier:** if someone sent you a **Custom GPT link** for this tool, just open it and type `Start quick discovery`. There's nothing to set up.

---

## What you'll say to it

| Say | What happens |
|---|---|
| `Start quick discovery` | It begins: one short question at a time |
| `What do you already know?` | A short summary, with no new questions |
| `What's missing?` | The most important gaps, with no new questions |
| `Stop`, or `Generate snapshot` | It stops and gives you the report file |
| `Generate final report` | The full detailed report |
| `Resume discovery` (with your report file attached) | It continues where you left off |
| `Deepen discovery` | An optional second, deeper round, only if you ask for it |
| `Check setup` | It confirms its files are in place |

**Keep the report file it gives you.** That file is your saved progress. Share it with whoever you choose. The tool never sends it anywhere.

## Included / you supply / not included

- **Included:** the interviewer's rules, the 269-question bank, a frozen scoring rubric, and a checker (`validate_coverage.py`) that verifies the report's coverage math wherever the AI can run Python.
- **You supply:** your own answers. If you like, you can also share files such as a sample script or a CRM screenshot. It ships with **no facts about any business**.
- **Not included, on purpose:** advice, coaching, script rewriting, outreach to anyone, changes to your CRM or systems, or legal conclusions. It documents. It doesn't prescribe.

**Privacy:** it only asks for examples with names removed. It never asks for SSNs, tax returns, credit reports, account numbers or client records.

---

## For builders

- [SETUP.md](SETUP.md): the step-by-step guide the AI follows during setup.
- [GPT_SETUP.md](GPT_SETUP.md): how to publish it as a one-link Custom GPT.
- [TESTING.md](TESTING.md): the smoke test to run in a fictional Project before you share it.
- `project-files/`: the five files that go into a Project or GPT, which are also attached to each [release](https://github.com/lantonior80/business-discovery-tool/releases/latest).
- `instructions/PROJECT_INSTRUCTIONS.txt`: the instructions to paste (under 8,000 characters, so they fit ChatGPT and Claude).
- `reference-js/`: the original JavaScript checker, which gives identical results.
- Run the tests: `python -m unittest discover -s tests`. They also compare the Python and JavaScript checkers when Node is installed.

Works with five files, so it fits even ChatGPT's free-plan limit of five files per Project. The checker needs Python 3.8+ and nothing else.

License: MIT (see [LICENSE](LICENSE)).
