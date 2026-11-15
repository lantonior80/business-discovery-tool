# Publish it as a Custom GPT (one link, nothing to set up)

Do this once from your own ChatGPT account. Building GPTs needs a paid plan. Then share the link: whoever opens it can start right away, with no files or settings.

1. Go to **chatgpt.com/gpts/editor** (or **Explore GPTs → Create**) and open the **Configure** tab.
2. **Name:** `Business Discovery Tool`.
   **Description:** `Maps how your real-estate team turns leads into buyers, one short question at a time, and saves a shareable report.`
3. **Instructions:** paste the full text of [`instructions/PROJECT_INSTRUCTIONS.txt`](instructions/PROJECT_INSTRUCTIONS.txt). It's under 8,000 characters, so it fits.
4. **Conversation starters:**
   - `Start quick discovery`
   - `What do you already know?`
   - `Resume discovery`
   - `Generate snapshot`
5. **Knowledge:** upload the five files from [`project-files/`](project-files) or the latest release: `DISCOVERY_GUIDE.md`, `QUESTION_BANK.md`, `COVERAGE_RUBRIC.json`, `MANIFEST.json`, `validate_coverage.py`.
6. **Capabilities:** turn **Code Interpreter & Data Analysis** **ON**, so the checker can run. Web search can stay off; the tool never browses for business facts.
7. Click **Create** (or **Update**). Choose **Anyone with the link**. Don't list it in the GPT Store unless you want to.
8. Copy the link and send it to the person who will answer the questions.

**Before you share it,** run the smoke test in [TESTING.md](TESTING.md) in your new GPT, using only made-up answers.

**Each new chat starts fresh.** That's normal. To continue a discovery, the person uploads the report file from last time and types `Resume discovery`.
