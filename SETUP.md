# Business Discovery Tool — setup guide (for the AI assistant)

**You are the AI assistant reading this because the person you're talking to pasted the setup paragraph.**
Walk them through the steps below. They are not technical. Rules for you:

- Give **one step at a time** in plain English, then wait for them to say "done" (or similar) before the next step.
- Do the thinking for them. Never ask them to edit a file or use a terminal.
- Chat apps can't add Project files or change Project settings by themselves, so **they click; you guide**. Tell them exactly what to click.
- If they can't find a button, ask them to paste a screenshot (on Windows: Windows + Shift + S, then Ctrl + V in the chat; on Mac: Cmd + Shift + 4, then paste) and point to it.
- Don't start the questionnaire until step 5. Don't ask them any business questions during setup.
- Keep a short checklist in your messages, e.g. "Step 2 of 5 ✅".

---

## Step 1 — Make sure we're inside a Project

Ask which app they're using: **ChatGPT** or **Claude**, and whether this chat is inside a Project (the Project's name shows at the top of the chat or in the sidebar).

- **Already in a Project:** go to step 2.
- **Not in a Project:**
  - **ChatGPT:** in the left sidebar click **New project**, name it `Business Discovery`, and create it. Open it and start a new chat inside it.
  - **Claude:** click **Projects** in the left sidebar, click **Create project**, name it `Business Discovery`, and create it.
  - Then ask them to paste the setup paragraph again in a chat inside that new Project, and continue there.
- **They'd rather not use Projects:** if whoever shared this tool gave them a Custom GPT link, they can just open that link and type `Start quick discovery`. Setup is then finished.

## Step 2 — Download the five tool files

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

## Step 3 — Add the five files to the Project

- **ChatGPT:** open the Project's page (click its name in the sidebar). Click **Add files** (it may be under the Project's **⋯** menu → **Files**). Choose all five files from Downloads, then wait until each shows as uploaded.
- **Claude:** open the Project. In the Project knowledge area on the right, click **+** / **Add content** → **Upload from device**, and select all five files.

Ask them to tell you when all **five** files appear in the Project's file list. If their plan allows fewer files and an upload is refused, tell them which file is missing. All five are required.

## Step 4 — Paste the instructions

Open the instructions file at https://raw.githubusercontent.com/lantonior80/business-discovery-tool/main/instructions/PROJECT_INSTRUCTIONS.txt. Show its **entire text exactly as written, inside one code block**, so they can use the code block's **Copy** button. Don't shorten it, summarize it or change any word. If you can't open that link, ask them to open it in their browser, press Ctrl + A (Cmd + A on a Mac) to select everything, and copy it.

Then:
- **ChatGPT:** on the Project's page, open the Project's **⋯** menu (or settings) → **Instructions**. Paste and click **Save**.
- **Claude:** on the Project's page, find **Project instructions** → **Edit** / **Set project instructions**. Paste and click **Save**.

## Step 5 — Check and start

Ask them to **start a new chat inside the Project**, since new instructions apply to new chats, and type:

```
Check setup
```

The tool should list the five files and, if a code tool is available, run its built-in check. If anything is missing, come back to this guide. When it says all five files are present, they type:

```
Start quick discovery
```

Tell them, in plain English, before you finish:
- It asks one short question at a time and takes about 12 minutes. "Skip" and "I don't know" are fine.
- They can say **Stop** at any time, and it saves a report file.
- **Keep the report file.** To continue another day, they start a new chat in the same Project, upload the file and type `Resume discovery`.

Setup is complete. You can stop here.
