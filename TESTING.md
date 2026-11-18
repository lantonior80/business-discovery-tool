# Smoke test, before you share the tool

Run this once in each new place you set it up (ChatGPT Project or Claude Project). Use a **separate test Project** and **only made-up answers**, and never mix test answers into a real person's discovery. It takes about 20 minutes. Mark each line ✅, ❌ or ⏸ (couldn't run).

## A. Setup (about 2 minutes, or 10 for the automated option)
- [ ] Paste the one-line setup command from the README into a fresh Project chat. The assistant asks **manual or automated**, then gives one step at a time and waits for you.
- [ ] **Manual:** all five files upload into the Project.
- [ ] **Automated (separate test Project):** in a Work-mode chat, ChatGPT starts without asking you to switch any mode; it asks you to sign in **in its browser window**, never in chat; after `done` it uploads all five files to Sources, saves the instructions, and gives you a fresh chat link without starting the questions.
- [ ] In a new chat, `Check setup` lists all five files. If code runs, it reports `"valid": true`, `204` questions and `362` facets. If code can't run, it says so plainly, and doesn't pretend it ran.

## B. Interview behavior (about 10 minutes)
- [ ] `Start quick discovery` → one short welcome that says about 13 questions and 20–25 minutes, suggests voice, says estimates and "skip" are fine, invites uploading a report or screenshot, and says you can Stop anytime. It then asks question 1 in the same message.
- [ ] Question 1 is the scripted opener: "Tell me about your business: in the last 12 months, about how many deals… how much commission… how much did the business keep… goal for the next 12 months?"
- [ ] Next, in order: how you get customers, how you make money, what's stopping you, why you want to grow, what would break if leads doubled, out of 100 leads how many go how far, why buyers don't move forward, first contact to signed contract, how you pay for growth, after contract and closing, your team, and 12 months from now.
- [ ] Each question comes with a short "what we mean" and examples that it calls **just examples**. Follow-ups ask only for what you left out, one at a time.
- [ ] Give made-up numbers. It **never comments** on them (no "that's good", no comparisons or ratios).
- [ ] It doesn't assume facts you never gave, such as how many agents or VAs you have or which CRM you use.
- [ ] When the conversation reaches appointments, it asks **how many appointments a prospect has before signing a contract** and what type each one is, unless you already said. It never says "appointment 1/2" or "video call" unless you did. Before asking what each agent owns, it asks how many agents you have.
- [ ] Answer "I don't know" once and "skip" once. It accepts both and moves on.
- [ ] It never re-asks something you already answered.
- [ ] After question 13 it stops asking on its own and gives you the file, with no extra questions.

## C. Stop, export and resume (about 8 minutes)
- [ ] In a second test chat, answer two questions, then say `Stop`. You get the report with **no** extra question and no "want to continue?".
- [ ] The report is one Markdown file named like `Business_Discovery_<Team>_<date>_v01.md`. It downloads and opens.
- [ ] The report contains your original answers, what's covered and what's missing, the full question list, and a checkpoint section.
- [ ] The report has **no evaluation**: no scores, diagnosis, "biggest problem", benchmarks or advice. Its message tells you to send the file to the person who shared the tool with you, and says a PDF copy is available on request.
- [ ] It states the validation result honestly: either the checker's real result, or exactly `structured-review-only; executable validation unverified; automated acceptance pending`.
- [ ] New chat: upload that file and type `Resume discovery`. It remembers your answers and its count, and it doesn't start over or re-ask anything.
- [ ] Resume the file from the six-answer chat (part B). It says the round is finished and asks **no** new question. It doesn't start a deeper round by itself.
- [ ] Say "no thanks" to a deeper round, save, then resume. It still remembers that you declined.
- [ ] `What do you already know?` and `What's missing?` give summaries with **no** new question.

## D. Privacy
- [ ] Ask it to send the report to someone. It declines and tells you to share the file yourself.
- [ ] It never asks for SSNs, tax returns, credit reports, account numbers or client names.

## E. Pilot with 3–5 real owners (before sharing widely)
Send the invitation from [handout/INVITE_MESSAGE.md](handout/INVITE_MESSAGE.md) to 3–5 friendly owners. For each one, note:
- [ ] Did they finish setup? If not, at which step did they stop (sign-in, Project, Work mode, pasting the line, uploads)?
- [ ] Did they finish the 13 questions? If not, which question did they stop at?
- [ ] How long did it take? Did they use voice?
- [ ] Which questions confused them, or got "I don't know"?
- [ ] Did they send you the file?

If most people stop during setup, fix how owners get to the tool before changing any questions.

## Result
- **All ✅:** ready to share.
- **Any ❌:** note which line and what happened, then fix it before sharing.
- **⏸ on the code check only:** fine. Reports will be labelled "structured-review-only".
