import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "project-files"
# Rule tests use a frozen copy of the 1.1.0 questions: the checker logic is the same for any package,
# and these tests rely on specific 1.1.0 questions that later releases retired.
FIXTURE = ROOT / "tests" / "fixtures" / "pkg-1.1.0"
sys.path.insert(0, str(PROJECT))

import validate_coverage as vc  # noqa: E402

PKG = vc.load_package(str(FIXTURE))
_BLANK = vc.blank_assessment(PKG)


def fresh():
    return copy.deepcopy(_BLANK)


def row(a, qid):
    return next(q for q in a["assessments"] if q["question_id"] == qid)


def facet(a, qid, i=0):
    return row(a, qid)["facet_results"][i]


def validate(a, binding=None):
    return vc.validate_assessment(a, PKG, binding)
