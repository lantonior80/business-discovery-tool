# Business Discovery Tool — setup guide (for the AI assistant)

**You are the AI assistant reading this because the person you're talking to pasted the setup line.**
Walk them through the steps below. They are not technical. Rules for you:

- Give **one step at a time** in plain English, then wait for them to say "done" (or similar) before the next step.
- Do the thinking for them. Never ask them to edit a file or use a terminal.
- In manual setup, chat apps can't add Project files or change Project settings by themselves, so **they click; you guide**. Tell them exactly what to click.
- If they can't find a button, ask them to paste a screenshot (on Windows: Windows + Shift + S, then Ctrl + V in the chat; on Mac: Cmd + Shift + 4, then paste) and point to it.
- Never ask for a password or verification code in chat.
- Don't start the questionnaire until setup is finished. Don't ask them any business questions during setup.
- Keep a short checklist in your messages, e.g. "Manual setup — step 2 of 4 ✅".

---

## Step 1 — Make sure we're inside a Project

Ask which app they're using: **ChatGPT** or **Claude**, and whether this chat is inside a Project (the Project's name shows at the top of the chat or in the sidebar).

- **Already in a Project:** go to step 2.
- **Not in a Project:**
  - **ChatGPT:** in the left sidebar, under **Projects**, click **+** to create a new project, name it `Business Discovery`, and click **Create project**. On the Project's page, select **Work** in the **Chat / Work** selector. There's no "New chat" button: they just type in the message box on that page.
  - **Claude:** click **Projects** in the left sidebar, click **+ New project**, name it `Business Discovery`, and click **Create project**. Then type in the message box on the Project's page.
  - Then ask them to paste the setup line again in that new Project chat, and continue there.
- **They'd rather not use Projects:** explain kindly that the tool needs a Project, because that's where its five files and instructions are kept so every future chat can use them.

## Step 2 — Let them choose: manual or automated

Show them this choice, in these words, and wait for their answer:

> **How would you like to set it up?**
>
> **A. Manual setup (about 5 minutes).** You download 5 files by clicking links, then upload them into this Project and paste one block of text. I'll tell you exactly what to click.
>
> **B. Automated setup (ChatGPT only).** I do the downloading and uploading for you. You just sign in to ChatGPT inside the browser window I open: your email, your password, and a verification code. If you've never set up a way to receive codes, you'll be asked to set one up then (a text message to your phone is usually easiest). If you already have one, the code is sent there.

- **Using Claude:** only option A is available. Say so, and go to A1.
- **A** → go to **A1**. **B** → go to **B1**.

---

## Manual setup (option A)

### A1 — Download the five tool files

Ask them to click each link below. Each one downloads a file, usually into their **Downloads** folder.

1. https://github.com/lantonior80/business-discovery-tool/releases/latest/download/DISCOVERY_GUIDE.md
2. https://github.com/lantonior80/business-discovery-tool/releases/latest/download/QUESTION_BANK.md
3. https://github.com/lantonior80/business-discovery-tool/releases/latest/download/COVERAGE_RUBRIC.json
4. https://github.com/lantonior80/business-discovery-tool/releases/latest/download/MANIFEST.json
5. https://github.com/lantonior80/business-discovery-tool/releases/latest/download/validate_coverage.py

Tell them:
- If the browser asks whether to keep a file, click **Keep**. All five are plain text files.
- If a link opens a page of text instead of downloading, they should go back and **right-click the link → Save link as…**.
- **Don't rename the files.** The tool checks them by their exact names.

The five separate links are usually easiest. If they prefer one download, there is a zip at https://github.com/lantonior80/business-discovery-tool/releases/latest/download/business-discovery-project-files.zip
which must be unzipped first: double-click it on a Mac, or right-click → **Extract All** on Windows.

### A2 — Add the five files to the Project

- **ChatGPT:** open the Project's page (click its name in the sidebar). Click **Sources** (or **Add files**; it may be under the Project's **⋯** menu), then **Add sources** → **Upload**. Choose all five files from Downloads, then wait until each shows as uploaded.
- **Claude:** open the Project. In the Project knowledge area on the right, click **+** / **Add content** → **Upload from device**, and select all five files.

Ask them to tell you when all **five** files appear in the Project's file list. If their plan allows fewer files and an upload is refused, tell them which file is missing. All five are required.

### A3 — Paste the instructions

Open the instructions file at https://raw.githubusercontent.com/lantonior80/business-discovery-tool/main/instructions/PROJECT_INSTRUCTIONS.txt. Show its **entire text exactly as written, inside one code block**, so they can use the code block's **Copy** button. Don't shorten it, summarize it or change any word. If you can't open that link, ask them to open it in their browser, press Ctrl + A (Cmd + A on a Mac) to select everything, and copy it.

Then:
- **ChatGPT:** on the Project's page, open the Project's **⋯** menu → **Project settings** → **Instructions**. Paste and click **Save**.
- **Claude:** on the Project's page, find **Project instructions** → **Edit** / **Set project instructions**. Paste and click **Save**.

Then go to **Step 3**.

---

## Automated setup (option B, ChatGPT only)

The person already switched this Project chat to **Work** mode before pasting the setup line, so you can do this yourself. Don't ask them to switch any mode.

### B1 — Tell them what will happen

In one short message, explain in plain English:
- You'll open a browser window and ask them to **sign in to ChatGPT** there. They may need to tap **Take over** to type in it.
- They enter their email and password, then a verification code. They pick how to receive the code: a text message to their phone is usually easiest. If they've never set this up, ChatGPT walks them through it first.
- They type passwords and codes **only in that browser window**, never in the chat.
- When signed in, they type **done** in the chat. You do the rest.

### B2 — Run the automated setup

Open https://raw.githubusercontent.com/lantonior80/business-discovery-tool/main/AGENT_SETUP.md and follow it yourself, starting with its step 1. It ends with its own check and a "Setup complete" summary. Setup is then finished (see Step 3).

**If you can't open or control a browser,** the chat is probably still in Chat mode. Tell them to switch the **Chat / Work** selector to **Work** and paste the setup line again, or offer **manual setup** and go to A1. Never leave them without a clear next action.

---

## Step 3 — Check and finish

**After automated setup:** you already ran this check and gave them the summary below. Nothing more to do.

**After manual setup:**
1. Ask them to **start a new chat inside the Project** (new instructions apply to new chats) and type `Check setup` there.
2. It should list the five files and, if a code tool is available, run its built-in check. Ask them to come back to **this** chat and tell you what it said (or paste a screenshot).
3. If anything is missing, go back to the step that fixes it (A2 for files, A3 for instructions).
4. When all five files are present, finish with this summary, filled in with what actually happened (never claim a check that didn't run):

> **Setup complete.**
> - All five files added to **<Project name>**.
> - Tool instructions saved.
> - Setup check: <passed: 204 questions, 362 facets | files present, but the code check couldn't run there>.
> - The questionnaire has **not** started.
>
> When you're ready, go to the chat where you typed `Check setup` and type `Start quick discovery`.

In that summary, write **only** `Start quick discovery` in code format (inside backticks), so they can tap it to copy. Everything else stays normal text.
> It asks about 13 short questions, one at a time, takes about 20–25 minutes (you can talk instead of typing), and accepts "skip" or "I don't know". Say **Stop** at any time to get your report file. **Keep that file:** to continue another day, start a new chat in the Project, upload it and type `Resume discovery`.

Setup is complete. You can stop here.
