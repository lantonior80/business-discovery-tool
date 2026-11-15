# Smoke test, before you share the tool

Run this once in each new place you set it up (ChatGPT Project, Custom GPT or Claude Project). Use a **separate test Project or GPT** and **only made-up answers**, and never mix test answers into a real person's discovery. It takes about 20 minutes. Mark each line ✅, ❌ or ⏸ (couldn't run).

## A. Setup (about 2 minutes)
- [ ] Paste the setup paragraph from the README into a fresh chat. The assistant gives one step at a time and waits for you.
- [ ] All five files upload into the Project, or into the GPT's Knowledge.
- [ ] In a new chat, `Check setup` lists all five files. If code runs, it reports `"valid": true`, `269` questions and `409` facets. If code can't run, it says so plainly, and doesn't pretend it ran.

## B. Interview behavior (about 10 minutes)
- [ ] `Start quick discovery` → a short intro, then **exactly one** question. No list of questions and no form.
- [ ] It doesn't assume facts you never gave, such as how many agents or VAs you have or which CRM you use.
- [ ] Answer "I don't know" once and "skip" once. It accepts both and moves on.
- [ ] It never re-asks something you already answered.
- [ ] After **six real answers**, when it can't time the chat, it stops asking on its own and gives a snapshot.

## C. Stop, export and resume (about 8 minutes)
- [ ] In a second test chat, answer two questions, then say `Stop`. You get the report with **no** extra question and no "want to continue?".
- [ ] The report is one Markdown file named like `Business_Discovery_<Team>_<date>_v01.md`. It downloads and opens.
- [ ] The report contains your original answers, what's covered and what's missing, the full question list, and a checkpoint section.
- [ ] It states the validation result honestly: either the checker's real result, or exactly `structured-review-only; executable validation unverified; automated acceptance pending`.
- [ ] New chat: upload that file and type `Resume discovery`. It remembers your answers and its count, and it doesn't start over or re-ask anything.
- [ ] Resume the file from the six-answer chat (part B). It says the round is finished and asks **no** new question. It doesn't start a deeper round by itself.
- [ ] Say "no thanks" to a deeper round, save, then resume. It still remembers that you declined.
- [ ] `What do you already know?` and `What's missing?` give summaries with **no** new question.

## D. Privacy
- [ ] Ask it to send the report to someone. It declines and tells you to share the file yourself.
- [ ] It never asks for SSNs, tax returns, credit reports, account numbers or client names.

## Result
- **All ✅:** ready to share.
- **Any ❌:** note which line and what happened, then fix it before sharing.
- **⏸ on the code check only:** fine. Reports will be labelled "structured-review-only".
