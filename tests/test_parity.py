"""Python checker must match the JavaScript original exactly. Skipped when Node is not installed."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _helpers import FIXTURE, PKG, PROJECT, ROOT, vc

NODE = shutil.which("node")
DRIVERS = ["test-validation.mjs", "test-d1.mjs", "review-fix-regressions.mjs", "review-reproductions-corrected.mjs"]
SHIM = """import fs from 'node:fs';
export * from './validate-coverage-orig.mjs';
import {validateAssessment as v0} from './validate-coverage-orig.mjs';
export function validateAssessment(a,pkg,binding=null){const out=v0(a,pkg,binding);fs.appendFileSync(process.env.PARITY_LOG,JSON.stringify({a,binding,out})+'\\n');return out;}
"""


@unittest.skipUnless(NODE, "Node is not installed; parity check skipped")
class Parity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="bdt-parity-"))
        for f in ["QUESTION_BANK.md", "COVERAGE_RUBRIC.json", "MANIFEST.json"]:
            shutil.copy(FIXTURE / f, cls.tmp / f)
        for f in DRIVERS:
            shutil.copy(ROOT / "reference-js" / f, cls.tmp / f)
        shutil.copy(ROOT / "reference-js" / "validate-coverage.mjs", cls.tmp / "validate-coverage-orig.mjs")
        (cls.tmp / "validate-coverage.mjs").write_text(SHIM, encoding="utf-8", newline="\n")
        (cls.tmp / "ASSESSMENT_TEMPLATE.json").write_bytes(cls.js("--template").stdout)
        cls.log = cls.tmp / "parity.jsonl"
        env = dict(os.environ, PARITY_LOG=str(cls.log))
        cls.driver_out = [subprocess.run([NODE, d], cwd=cls.tmp, env=env, capture_output=True, text=True) for d in DRIVERS]

    @classmethod
    def js(cls, *args):
        return subprocess.run([NODE, "validate-coverage-orig.mjs", *args], cwd=cls.tmp, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_js_suites_pass_on_shipped_files(self):
        for d, p in zip(DRIVERS, self.driver_out):
            self.assertEqual(p.returncode, 0, d + "\n" + p.stdout + p.stderr)

    def test_every_logged_case_identical(self):
        n = 0
        for line in self.log.read_text(encoding="utf-8").splitlines():
            rec = json.loads(line); n += 1
            py = vc.validate_assessment(rec["a"], PKG, rec["binding"])
            self.assertEqual(vc.stringify(py), vc.stringify(rec["out"]), "case %d differs" % n)
        self.assertGreaterEqual(n, 138)

    def test_cli_outputs_byte_identical(self):
        for args in (["--check-package"], ["--template"]):
            js = self.js(*args).stdout
            py = subprocess.run([sys.executable, "-I", str(PROJECT / "validate_coverage.py"), *args, "--dir", str(self.tmp)], capture_output=True).stdout
            self.assertEqual(py, js, args)

    def test_cli_outputs_byte_identical_on_shipped_package(self):
        tmp = Path(tempfile.mkdtemp(prefix="bdt-shipped-"))
        try:
            for f in ["QUESTION_BANK.md", "COVERAGE_RUBRIC.json", "MANIFEST.json"]:
                shutil.copy(PROJECT / f, tmp / f)
            shutil.copy(ROOT / "reference-js" / "validate-coverage.mjs", tmp / "validate-coverage.mjs")
            for args in (["--check-package"], ["--template"]):
                js = subprocess.run([NODE, "validate-coverage.mjs", *args], cwd=tmp, capture_output=True).stdout
                py = subprocess.run([sys.executable, "-I", str(PROJECT / "validate_coverage.py"), *args, "--dir", str(tmp)], capture_output=True).stdout
                self.assertTrue(js)
                self.assertEqual(py, js, args)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
