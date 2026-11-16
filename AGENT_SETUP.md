# Business Discovery Tool — automated setup runbook (for ChatGPT in Work mode)

**You are ChatGPT in a Work-mode Project chat, with a cloud browser.** The person chose the **automated setup**. You do the work in your cloud browser: download the five files, add them to their Project's Sources, save the Project instructions and check the setup. The person only signs in to ChatGPT inside your browser. They are not technical: one short message at a time, in plain English.

## Rules
- Never ask for their password or verification code in chat. They type those **only** in your browser, during the sign-in handoff.
- Don't promise which verification method appears. The live sign-in page decides (text message, authenticator app, email, etc.).
- Don't start the questionnaire. Don't ask business questions. Never type `Start quick discovery` for them.
- Don't ask questions you can answer yourself. The only things you need from them are the sign-in and, rarely, a decision about existing Project instructions.
- Don't delete or replace anything that's already in their Project without asking first.
- Labels, buttons and tool APIs change. Read the live page and your live tool documentation; the code below is only an example from a successful run.

## 1. Use this Project
Install into the Project this chat is in. **Don't ask which Project, and don't ask for permission:** they made this Project for the tool, and choosing automated setup is their yes. Note its name and go straight on.

Never end a message by announcing what you will do next. Either do it, or end with exactly one clear thing for them to do (for example "Sign in, then type **done**").

## 2. Download and verify the five files
From https://github.com/lantonior80/business-discovery-tool/releases/latest download, all from the **same** release:

`DISCOVERY_GUIDE.md`, `QUESTION_BANK.md`, `COVERAGE_RUBRIC.json`, `MANIFEST.json`, `validate_coverage.py`, plus `SHA256SUMS.txt`.

Check each file is non-empty and its SHA-256 matches `SHA256SUMS.txt`. Don't rename or edit them. Stop on any mismatch and download that file again. Record the release tag.

## 3. Hand sign-in to the person
1. Open https://chatgpt.com in your cloud browser (not any other browser session).
2. If it already shows their account and this Project, skip to step 4.
3. Otherwise open **Log in** and hand the browser to them for authentication (for example `tab.requestUserTakeover("authentication")`). Send them this message:

   > Please sign in to ChatGPT in the browser window I just opened. Tap **Take over** if you see it. Enter your email and password. ChatGPT will then ask for a code: choose how to receive it (a text message to your phone is usually easiest). If you've never set up a way to get codes, it will ask you to set one up now: follow its steps. When you're signed in, type **done** here.

4. After "done", read the page. Require real signed-in evidence and this Project visible in the sidebar. "Done" alone is not proof. Reuse this tab; don't start a second sign-in.

## 4. Upload the five files to the Project's Sources
1. Open the Project (sidebar → its name → **Project home**) and confirm the heading matches.
2. Open **Sources** and read the list first. If matching files already exist, compare them; don't duplicate or delete unrelated files.
3. Put the five verified files in the folder your browser's file chooser can see (in a successful run: a shared directory such as `/workspace/shared/business-discovery/`). Confirm the staged bytes still match.
4. **Add sources** → **Upload**. Start waiting for the file-chooser event *before* clicking Upload, then pass all five paths (or one at a time if the chooser takes only one). Upload into Project Sources, never into the chat box.
5. Wait until processing finishes. "Adding…" is not finished. Require all five exact names as completed rows with no errors.

## 5. Save the Project instructions
1. Read the full text of https://raw.githubusercontent.com/lantonior80/business-discovery-tool/main/instructions/PROJECT_INSTRUCTIONS.txt. Use it word for word; don't summarize. Don't add it as a sixth Source.
2. Project's **⋯** menu → **Project settings** → **Instructions**. Read the field's actual value.
3. If it already contains text, show the person and ask: replace or combine? Keep the old text until they decide.
4. Fill in the exact text, compare the field with it, click **Save**, wait for it to finish, reopen settings and confirm it saved. Change nothing else.

## 6. Check setup in a fresh chat
1. Start a **new chat inside the Project** (not this agent chat). Type `Check setup` and send once.
2. Wait for the complete answer. It should list all five files and say whether it ran `python validate_coverage.py --check-package` (expected: valid, 269 questions, 409 facets).
3. A checker pass alone is not enough. Require both: all five completed rows in Sources (step 4) **and** all five files readable in the fresh chat. If code can't run there, say so plainly; don't claim it ran.

## 7. Hand back
- Leave the Sources page showing the five files and take a screenshot as proof (hide unrelated chats).
- Tell the person, in plain English: setup is done; open the fresh chat (give its link) and type `Start quick discovery` when ready. Write **only** `Start quick discovery` in code format (inside backticks) so they can tap it to copy; everything else is normal text. It asks one short question at a time, takes about 12 minutes, accepts "skip" and "I don't know", and **Stop** saves a report file they should keep. To continue later: new chat in the Project, upload the report, type `Resume discovery`.
- Report honestly what was verified and anything that wasn't. Don't call setup complete if a file, the saved instructions or the check is missing.

## Checklist
- [ ] Correct account and Project confirmed after sign-in
- [ ] Five files from one release, hashes match `SHA256SUMS.txt`
- [ ] Five completed rows in Project Sources, no errors
- [ ] Exact instructions saved, confirmed by reopening settings
- [ ] Fresh Project chat reads all five files; checker result recorded truthfully
- [ ] No discovery questions asked; person given the chat link and `Start quick discovery`
