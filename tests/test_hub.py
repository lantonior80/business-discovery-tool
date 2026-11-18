"""Rules for the hub itself: five files, hashes, instruction length, links, no private data."""
import re
import subprocess
import unittest

from _helpers import PROJECT, ROOT, vc

FILES = ["DISCOVERY_GUIDE.md", "QUESTION_BANK.md", "COVERAGE_RUBRIC.json", "MANIFEST.json", "validate_coverage.py"]
INSTR = ROOT / "instructions" / "PROJECT_INSTRUCTIONS.txt"
# Words that must never appear in the public tool (private origin, people, fictional QA case).
FORBIDDEN = ["Liliana", "Alder Lane", "Northmere", "husband", "Southern California", "GoHighLevel", "Hormozi", "Krista", "P27", "C:\\Users", "/Users/", "useai", "Analisys", "g-p-"]


def tracked_text_files():
    try:
        out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
        paths = [ROOT / p for p in out]
    except Exception:
        paths = [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts]
    return [p for p in paths if p.suffix in (".md", ".txt", ".json", ".py", ".mjs", "") and p.is_file()]


class Hub(unittest.TestCase):
    def test_exactly_five_project_files(self):
        self.assertEqual(sorted(p.name for p in PROJECT.iterdir() if p.is_file()), sorted(FILES))

    def test_package_loads_and_hashes_match(self):
        pkg = vc.load_package(str(PROJECT))
        self.assertEqual(len(pkg["rubric"]["questions"]), 332)
        self.assertEqual(sum(len(q["facets"]) for q in pkg["rubric"]["questions"]), 538)

    def test_instructions_fit_8000_chars(self):
        text = INSTR.read_text(encoding="utf-8")
        self.assertLess(len(text), 8000)
        for f in FILES:
            self.assertIn(f, text, "instructions must name " + f)
        self.assertIn("structured-review-only; executable validation unverified; automated acceptance pending", text)

    def test_setup_links_match_files(self):
        setup = (ROOT / "SETUP.md").read_text(encoding="utf-8")
        linked = re.findall(r"releases/latest/download/([A-Za-z_.-]+)", setup)
        self.assertEqual(sorted(set(linked) - {"business-discovery-project-files.zip"}), sorted(FILES))
        self.assertIn("instructions/PROJECT_INSTRUCTIONS.txt", setup)

    def test_readme_paragraph_points_to_setup(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("raw.githubusercontent.com/lantonior80/business-discovery-tool/main/SETUP.md", readme)

    def test_setup_offers_manual_and_automated(self):
        setup = (ROOT / "SETUP.md").read_text(encoding="utf-8")
        for s in ("Manual setup", "Automated setup", "main/AGENT_SETUP.md"):
            self.assertIn(s, setup)
        agent = (ROOT / "AGENT_SETUP.md").read_text(encoding="utf-8")
        self.assertIn("instructions/PROJECT_INSTRUCTIONS.txt", agent)
        self.assertIn("SHA256SUMS.txt", agent)
        for f in FILES:
            self.assertIn(f, agent)

    def test_opening_maps_lead_sources_first(self):
        guide = (PROJECT / "DISCOVERY_GUIDE.md").read_text(encoding="utf-8")
        opening = guide.index("### Opening — how strangers find the business")
        money = guide.index("### Money basics (always next, after the opening)")
        self.assertLess(opening, money)
        self.assertLess(money, guide.index("After the opening and money basics, choose the highest-value"))
        for qid in ("Q02.01", "Q02.02", "Q02.03", "Q02.04", "Q03.01", "Q03.02"):
            self.assertIn(qid, guide[opening:money])
        for qid in ("Q17.01", "Q17.02", "Q17.03", "Q17.04"):
            self.assertIn(qid, guide[money:money + 3000])
        self.assertIn("not** count toward the 12-minute budget or the six-answer fallback", guide)
        instr = INSTR.read_text(encoding="utf-8")
        self.assertIn("how strangers find the business", instr)
        self.assertIn("money basics", instr)

    def test_new_modules_and_facts_only_handoff(self):
        bank = (PROJECT / "QUESTION_BANK.md").read_text(encoding="utf-8")
        self.assertIn("## MODULE 17 —", bank)
        self.assertIn("<!-- Q17.33 -->", bank)
        self.assertIn("<!-- Q18.30 -->", bank)
        guide = (PROJECT / "DISCOVERY_GUIDE.md").read_text(encoding="utf-8")
        self.assertNotIn("Preliminary diagnostic observations", guide)
        self.assertNotIn("failure point, strongest alternative explanation", guide)
        line = "Download this file and send it to the person who shared this tool with you."
        self.assertIn(line, guide)
        self.assertIn(line, INSTR.read_text(encoding="utf-8"))

    def test_relative_links_exist(self):
        for md in ROOT.glob("*.md"):
            for target in re.findall(r"\]\(([^)#:]+)\)", md.read_text(encoding="utf-8")):
                self.assertTrue((ROOT / target).exists(), f"{md.name} links to missing {target}")

    def test_no_private_or_origin_data(self):
        for p in tracked_text_files():
            if p.name == "test_hub.py":
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
            for bad in FORBIDDEN:
                self.assertNotIn(bad, text, f"{bad!r} found in {p.relative_to(ROOT)}")


if __name__ == "__main__":
    unittest.main()
