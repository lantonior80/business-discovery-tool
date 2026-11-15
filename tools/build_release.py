"""Build the release folder dist/: the five Project files, one zip of them, and SHA-256 checksums.

  python tools/build_release.py           # verify hashes, build dist/
  python tools/build_release.py --rehash  # after an intentional bank/rubric change: rewrite MANIFEST hashes first
"""
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "project-files"
DIST = ROOT / "dist"
FILES = ["DISCOVERY_GUIDE.md", "QUESTION_BANK.md", "COVERAGE_RUBRIC.json", "MANIFEST.json", "validate_coverage.py"]
ZIP = "business-discovery-project-files.zip"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    man_path = PROJECT / "MANIFEST.json"
    man = json.loads(man_path.read_text(encoding="utf-8"))
    bank, rubric = sha(PROJECT / "QUESTION_BANK.md"), sha(PROJECT / "COVERAGE_RUBRIC.json")
    if "--rehash" in sys.argv:
        man["bank_sha256"], man["rubric_sha256"] = bank, rubric
        man_path.write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print("MANIFEST hashes rewritten")
    elif (man["bank_sha256"], man["rubric_sha256"]) != (bank, rubric):
        sys.exit("Hash mismatch: the bank or rubric changed. If intentional, rerun with --rehash, then run the tests.")
    sys.path.insert(0, str(PROJECT))
    import validate_coverage as vc
    vc.load_package(str(PROJECT))  # raises on any package problem

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    for f in FILES:
        shutil.copy2(PROJECT / f, DIST / f)
    with zipfile.ZipFile(DIST / ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for f in FILES:
            z.write(PROJECT / f, f)
    shutil.copy2(ROOT / "instructions" / "PROJECT_INSTRUCTIONS.txt", DIST / "PROJECT_INSTRUCTIONS.txt")
    lines = [f"{sha(DIST / f)}  {f}" for f in FILES + [ZIP, "PROJECT_INSTRUCTIONS.txt"]]
    (DIST / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    print("dist/ ready")


if __name__ == "__main__":
    main()
