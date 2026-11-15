import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "project-files"
sys.path.insert(0, str(PROJECT))

import validate_coverage as vc  # noqa: E402

PKG = vc.load_package(str(PROJECT))
_BLANK = vc.blank_assessment(PKG)


def fresh():
    return copy.deepcopy(_BLANK)


def row(a, qid):
    return next(q for q in a["assessments"] if q["question_id"] == qid)


def facet(a, qid, i=0):
    return row(a, qid)["facet_results"][i]


def validate(a, binding=None):
    return vc.validate_assessment(a, PKG, binding)
