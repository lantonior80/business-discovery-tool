# Business Discovery Tool

**A friendly AI interviewer that maps how a real-estate team turns leads into buyers, one short question at a time, and saves the answers as a shareable report.**

It works inside a **ChatGPT Project** or a **Claude Project**. The owner just chats with it, by typing or voice. Behind the scenes it tracks 269 discovery questions, never asks the same thing twice, stops after about 12 minutes, and hands back one report file that can be picked up again later.

---

## Start here (about 2 minutes)

### Step 1 — Open ChatGPT
- Go to **chatgpt.com** and sign in, or sign up (it's free) if you don't have an account yet.

### Step 2 — Make a new Project
1. Tap the **three-line menu (☰)** on the left to open the side menu.
2. Find **Projects** and tap **+** next to it to create a new project.
3. Type the name: `Business Discovery`
4. Tap **Create project**.

### Step 3 — Switch to Work mode
1. You're now on the Project's page, with its name at the top.
2. Find the **Chat / Work** mode selector and select **Work** (not Chat).

### Step 4 — Start the setup
1. There's **no "New chat" button** here. Just tap the **message box** on this page, where you'd normally type to ChatGPT.
2. Copy the line in the gray box below. Tap the **copy icon** (two small squares) at its right.
3. Paste it into the message box and press **Enter** (or tap the send arrow).

```text
Set me up with the Business Discovery Tool by following this guide step by step: https://raw.githubusercontent.com/lantonior80/business-discovery-tool/main/SETUP.md
```

**That's it.** ChatGPT now asks how you'd like to set it up:

- **A. Manual:** you download 5 files and upload them into the Project. ChatGPT tells you exactly what to click.
- **B. Automated (ChatGPT, Work mode):** ChatGPT does the files for you. You only sign in to ChatGPT in the browser window it opens, with your email, password and a verification code (it can text one to your phone).

Either way, do what it says, one step at a time, then type `done`.

<details>
<summary>Using Claude instead of ChatGPT?</summary>

1. Go to **claude.ai** and sign in, or sign up (it's free) if you don't have an account yet.
2. In the menu on the left, tap **Projects**.
3. Tap **+ New project** (top right). Type the name `Business Discovery`, then tap **Create project**.
4. On the Project's page, tap the **message box**, paste the text from the gray box above, and press **Enter**.

</details>

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

- [SETUP.md](SETUP.md): the step-by-step guide the AI follows during setup (manual or automated).
- [AGENT_SETUP.md](AGENT_SETUP.md): the runbook ChatGPT (Work mode) follows for the automated setup.
- [TESTING.md](TESTING.md): the smoke test to run in a fictional Project before you share it.
- `project-files/`: the five files that go into a Project, which are also attached to each [release](https://github.com/lantonior80/business-discovery-tool/releases/latest).
- `instructions/PROJECT_INSTRUCTIONS.txt`: the instructions to paste (under 8,000 characters, so they fit ChatGPT and Claude).
- `reference-js/`: the original JavaScript checker, which gives identical results.
- Run the tests: `python -m unittest discover -s tests`. They also compare the Python and JavaScript checkers when Node is installed.

Works with five files, so it fits even ChatGPT's free-plan limit of five files per Project. The checker needs Python 3.8+ and nothing else.

License: MIT (see [LICENSE](LICENSE)).
