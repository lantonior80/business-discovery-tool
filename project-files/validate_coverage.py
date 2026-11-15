#!/usr/bin/env python3
"""Business Discovery Tool - coverage validator (Python edition).

A line-for-line port of validate-coverage.mjs so it runs anywhere Python 3.8+ runs,
including ChatGPT's and Claude's built-in code tools. Standard library only, no network.

Usage:
  python validate_coverage.py --check-package
  python validate_coverage.py --template [new.json]
  python validate_coverage.py assessment.json [new-result.json] [--sources source-map.json]
  (add --dir <folder> if the package files are not next to this script)

Exit 0 = VALID, 1 = assessment INVALID, 2 = package/JSON/file/CLI problem.
It checks structural consistency only. It cannot prove that evidence truly answers a question.
"""
import hashlib
import json
import math
import os
import re
import sys

PACKAGE_FILES = ("MANIFEST.json", "COVERAGE_RUBRIC.json", "QUESTION_BANK.md")


class _Undefined:
    """Stands in for JavaScript `undefined` (a key that is absent)."""
    _inst = None

    def __new__(cls):
        if cls._inst is None:
            cls._inst = super().__new__(cls)
        return cls._inst

    def __repr__(self):
        return "undefined"


UNDEF = _Undefined()

# --------------------------------------------------------------------------- JS helpers


def jget(o, k):
    if isinstance(o, dict):
        return o.get(k, UNDEF)
    return UNDEF


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def is_obj(v):
    """`v && typeof v === 'object'` (arrays included)."""
    return isinstance(v, (dict, list))


def truthy(v):
    if v is None or v is UNDEF or v is False:
        return False
    if is_num(v):
        return v != 0 and not (isinstance(v, float) and math.isnan(v))
    if isinstance(v, str):
        return len(v) > 0
    return True


def jeq(a, b):
    """Strict equality (===) for JSON values; objects compare by identity."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a is b
    if is_num(a) and is_num(b):
        return a == b
    if isinstance(a, str) and isinstance(b, str):
        return a == b
    if a is None or b is None or a is UNDEF or b is UNDEF:
        return a is b
    return a is b


def jin(v, arr):
    return any(jeq(v, x) for x in arr)


def jkey(v):
    """Map/Set key with SameValueZero semantics."""
    if isinstance(v, bool):
        return ("b", v)
    if is_num(v):
        return ("n", float(v))
    if isinstance(v, str):
        return ("s", v)
    if v is None:
        return ("null",)
    if v is UNDEF:
        return ("undef",)
    return ("o", id(v))


def js_num_str(n):
    if isinstance(n, float):
        if math.isnan(n):
            return "NaN"
        if math.isinf(n):
            return "Infinity" if n > 0 else "-Infinity"
        if n.is_integer() and abs(n) < 1e21:
            return str(int(n))
        return repr(n)
    return str(n)


def js_str(v):
    """String(v) / string concatenation."""
    if isinstance(v, str):
        return v
    if v is UNDEF:
        return "undefined"
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if is_num(v):
        return js_num_str(v)
    if isinstance(v, list):
        return ",".join("" if (x is None or x is UNDEF) else js_str(x) for x in v)
    return "[object Object]"


def _strip_undef(v):
    if isinstance(v, dict):
        return {k: _strip_undef(x) for k, x in v.items() if x is not UNDEF}
    if isinstance(v, list):
        return [None if x is UNDEF else _strip_undef(x) for x in v]
    if isinstance(v, float) and v.is_integer() and abs(v) < 1e21:
        return int(v)
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    return v


def stringify(v, indent=None):
    """JSON.stringify(v[, null, indent])."""
    if v is UNDEF:
        return None
    v = _strip_undef(v)
    if indent is None:
        return json.dumps(v, ensure_ascii=False, separators=(",", ":"))
    return json.dumps(v, ensure_ascii=False, indent=indent)


def same(a, b):
    return stringify(a) == stringify(b)


_JS_WS = " \t\n\r\v\f                 　﻿"


def nonempty(x):
    return isinstance(x, str) and len(x.strip(_JS_WS)) > 0


def to_number(v):
    if is_num(v):
        return float(v)
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    if v is None:
        return 0.0
    if isinstance(v, str):
        t = v.strip(_JS_WS)
        if t == "":
            return 0.0
        try:
            return float(t)
        except ValueError:
            return float("nan")
    return float("nan")


def js_ge(a, b):
    if isinstance(a, str) and isinstance(b, str):
        return a >= b
    x, y = to_number(a), to_number(b)
    return not (math.isnan(x) or math.isnan(y)) and x >= y


def js_lt(a, b):
    if isinstance(a, str) and isinstance(b, str):
        return a < b
    x, y = to_number(a), to_number(b)
    return not (math.isnan(x) or math.isnan(y)) and x < y


def js_le(a, b):
    if isinstance(a, str) and isinstance(b, str):
        return a <= b
    x, y = to_number(a), to_number(b)
    return not (math.isnan(x) or math.isnan(y)) and x <= y


def is_integer(v):
    return is_num(v) and math.isfinite(v) and float(v).is_integer()


def is_finite(v):
    return is_num(v) and math.isfinite(v)


def unique(seq):
    seen, out = set(), []
    for x in seq:
        k = jkey(x)
        if k not in seen:
            seen.add(k)
            out.append(x)
    return out


# --------------------------------------------------------------------------- package


def sha256(b):
    if isinstance(b, str):
        b = b.encode("utf-8")
    return hashlib.sha256(b).hexdigest()


def _reject_constant(name):
    raise ValueError("Unexpected token " + name + " in JSON")


def parse_json_bytes(b):
    t = b.decode("utf-8")
    if t.startswith("﻿"):
        t = t[1:]
    return json.loads(t, parse_constant=_reject_constant)


def parse(path):
    with open(path, "rb") as fh:
        return parse_json_bytes(fh.read())


MISSING_CODES = ["no_answer", "incomplete_component", "qualifier_unknown", "qualifier_contradicted", "bounds_unknown", "bounds_mismatch", "unresolved_conflict"]
_BANK_RE = re.compile(r"<!-- (Q[0-9]{2}\.[0-9]{2}) -->\s*[0-9]+\. \*\*\[([EDO])\]\*\* ([^\r\n]+)")


def find_package_dir(explicit=None):
    candidates = [explicit] if explicit else []
    candidates += [os.path.dirname(os.path.abspath(__file__)), os.getcwd(), "/mnt/data", "/mnt/user-data", "/mnt/user-data/uploads"]
    for d in candidates:
        if d and all(os.path.isfile(os.path.join(d, f)) for f in PACKAGE_FILES):
            return d
    raise RuntimeError("Package files not found. Put MANIFEST.json, COVERAGE_RUBRIC.json and QUESTION_BANK.md next to this script or pass --dir <folder>.")


def load_package(dir=None):
    d = find_package_dir(dir)
    manifest = parse(os.path.join(d, "MANIFEST.json"))
    rubric = parse(os.path.join(d, "COVERAGE_RUBRIC.json"))
    with open(os.path.join(d, "QUESTION_BANK.md"), "rb") as fh:
        bank = fh.read()
    with open(os.path.join(d, "COVERAGE_RUBRIC.json"), "rb") as fh:
        rubric_bytes = fh.read()
    errors = []
    if sha256(bank) != jget(manifest, "bank_sha256"):
        errors.append("QUESTION_BANK.md: immutable bank hash mismatch")
    if sha256(rubric_bytes) != jget(manifest, "rubric_sha256"):
        errors.append("COVERAGE_RUBRIC.json: frozen rubric hash mismatch")
    qs = [{"question_id": m.group(1), "priority": m.group(2), "question_text": m.group(3)} for m in _BANK_RE.finditer(bank.decode("utf-8"))]
    if len(qs) != 269 or not jeq(jget(manifest, "question_count"), 269) or not same(qs, jget(manifest, "question_manifest")):
        errors.append("MANIFEST: exact 269 IDs/text/priorities do not match bank")
    questions = jget(rubric, "questions")
    if not isinstance(questions, list) or len(questions) != 269:
        errors.append("RUBRIC: exactly 269 questions required")
    seen_q, seen_f = set(), set()
    for i, q in enumerate(questions if isinstance(questions, list) else []):
        qid = jget(q, "question_id")
        if jkey(qid) in seen_q:
            errors.append(js_str(qid) + ": duplicate rubric question")
        seen_q.add(jkey(qid))
        if not same({"question_id": qid, "priority": jget(q, "priority"), "question_text": jget(q, "question_text")}, qs[i] if i < len(qs) else UNDEF):
            errors.append(js_str(qid) + ": exact manifest mismatch")
        if not jin(jget(q, "mode"), ["factual", "evaluative", "mixed"]):
            errors.append(js_str(qid) + ": invalid mode")
        facets = jget(q, "facets")
        if not isinstance(facets, list) or not facets:
            errors.append(js_str(qid) + ": empty facets")
        for f in facets if isinstance(facets, list) else []:
            fid = jget(f, "facet_id")
            if not nonempty(fid) or jkey(fid) in seen_f:
                errors.append(js_str(qid) + ": invalid/duplicate facet ID")
            seen_f.add(jkey(fid))
            if not nonempty(jget(f, "proposition")) or not isinstance(jget(f, "required_for_full"), bool) or not isinstance(jget(f, "allows_some"), bool):
                errors.append(js_str(fid) + ": invalid facet definition")
            if not jin(jget(f, "mode"), ["factual", "evaluative", "mixed"]) or not jin(jget(f, "scope_policy"), ["general_required", "general_for_complete", "bounded_answer"]):
                errors.append(js_str(fid) + ": invalid mode/scope")
            seen = set()
            mq = jget(f, "material_qualifiers")
            for z in (mq if isinstance(mq, list) else []):
                zid = jget(z, "qualifier_id")
                if not nonempty(zid) or jkey(zid) in seen or not nonempty(jget(z, "requirement")):
                    errors.append(js_str(fid) + ": invalid qualifier")
                seen.add(jkey(zid))
            for k in ["actor", "event", "population", "time", "unit"]:
                if not nonempty(jget(jget(f, "bounds"), k)):
                    errors.append(js_str(fid) + ": missing bound " + k)
    if errors:
        raise RuntimeError("\n".join(errors))
    return {"manifest": manifest, "rubric": rubric}


# --------------------------------------------------------------------------- assessment


def expected_missing(f):
    out = []
    ext = jget(f, "extent")
    if jeq(ext, "none"):
        out.append({"code": "no_answer"})
    if jeq(ext, "some"):
        out.append({"code": "incomplete_component"})
    qrs = jget(f, "qualifier_results")
    for q in [q for q in (qrs if isinstance(qrs, list) else []) if is_obj(q)]:
        res = jget(q, "result")
        if jin(res, ["unknown", "contradicted"]):
            out.append({"code": "qualifier_" + js_str(res), "qualifier_id": jget(q, "qualifier_id")})
    br = jget(f, "bounds_result")
    if jin(br, ["unknown", "mismatch"]):
        out.append({"code": "bounds_" + js_str(br)})
    if jeq(jget(f, "conflict"), "unresolved"):
        out.append({"code": "unresolved_conflict"})
    return out


def _canonical_missing(a):
    return sorted(stringify(x) for x in a)


def default_independent_state():
    return {"applicability": {"status": "unknown", "evidence_refs": [], "reason": "Not assessed", "scope": "Unknown"}, "deferred": False, "defer_reason": "", "not_tracked": False, "not_tracked_reason": "", "conflicts": []}


def blank_assessment(pkg=None):
    pkg = pkg or load_package()
    m = pkg["manifest"]
    rows = []
    for q in pkg["rubric"]["questions"]:
        frs = []
        for f in q["facets"]:
            r = {"facet_id": f["facet_id"], "extent": "none", "evidence_refs": [],
                 "qualifier_results": [{"qualifier_id": z["qualifier_id"], "result": "unknown", "evidence_refs": [], "basis": "Not established"} for z in f["material_qualifiers"]],
                 "bounds_result": "unknown", "bounds_explanation": "No answer evidence yet", "conflict": "none", "missing": [], "explanation": "No supported answer to this proposition"}
            if jeq(jget(f, "scope_evidence_role"), "answer_evidence_refs"):
                r["answer_evidence_refs"] = []
            if truthy(jget(f, "component_scope_required")):
                r["component_scope"] = "unknown"
                r["component_scope_basis"] = "No supported paperwork scope yet"
                r["component_scope_evidence_refs"] = []
            r["missing"] = expected_missing(r)
            frs.append(r)
        rows.append({"question_id": q["question_id"], "question_text": q["question_text"], "priority": q["priority"], "independent_state": default_independent_state(), "facet_results": frs})
    return {"schema_version": "1.0.0", "bank_sha256": m["bank_sha256"], "rubric_sha256": m["rubric_sha256"],
            "session": {"status": "stopped", "command": "Generate snapshot", "timing_reliable": False, "substantive_answers": 0, "budget_minutes": 12, "active_minutes": None, "pass": 1, "deepen_authorized": False, "pass2_declined": False, "emitted_questions": [], "exported": True},
            "evidence": [], "context": [], "assessments": rows}


_COMMANDS = {"discovery": "discovery", "start quick discovery": "start_quick_discovery", "what do you already know": "known_summary", "what's missing": "gap_summary", "generate snapshot": "snapshot", "pause discovery": "pause", "stop discovery": "stop", "stop": "stop", "generate final report": "final_report", "generate discovery report": "final_report", "resume discovery": "resume", "deepen discovery": "deepen", "show full questionnaire": "questionnaire"}


def normalize_command(value):
    if not isinstance(value, str):
        return None
    k = value.strip(_JS_WS).lower().replace("’", "'")
    k = re.sub(r"\s+", " ", k)
    k = re.sub(r"\?$", "", k)
    return _COMMANDS.get(k)


def _is_arr(v):
    return isinstance(v, list)


def _shape_errors(a, binding):
    errors = []

    def obj(v, p):
        if not isinstance(v, dict):
            errors.append(p + ": must be an object")
            return False
        return True

    def arr(v, p, visit=None):
        if not isinstance(v, list):
            errors.append(p + ": must be an array")
            return
        if visit:
            for i, x in enumerate(v):
                visit(x, p + "[" + str(i) + "]")

    if not obj(a, "assessment"):
        return errors
    arr(jget(a, "evidence"), "evidence", lambda e, p: obj(e, p))

    def ctx(c, p):
        if obj(c, p):
            arr(jget(c, "evidence_refs"), p + ".evidence_refs")
    arr(jget(a, "context"), "context", ctx)

    def row(q, p):
        if not obj(q, p):
            return
        z = jget(q, "independent_state")
        if obj(z, p + ".independent_state"):
            if obj(jget(z, "applicability"), p + ".applicability"):
                arr(jget(jget(z, "applicability"), "evidence_refs"), p + ".applicability.evidence_refs")

            def con(c, t):
                if obj(c, t):
                    arr(jget(c, "evidence_refs"), t + ".evidence_refs")
            arr(jget(z, "conflicts"), p + ".conflicts", con)

        def fac(f, t):
            if not obj(f, t):
                return
            arr(jget(f, "evidence_refs"), t + ".evidence_refs")
            if jget(f, "answer_evidence_refs") is not UNDEF:
                arr(jget(f, "answer_evidence_refs"), t + ".answer_evidence_refs")

            def qual(zz, u):
                if obj(zz, u):
                    arr(jget(zz, "evidence_refs"), u + ".evidence_refs")
            arr(jget(f, "qualifier_results"), t + ".qualifier_results", qual)
            arr(jget(f, "missing"), t + ".missing", lambda m, u: obj(m, u))
        arr(jget(q, "facet_results"), p + ".facet_results", fac)
    arr(jget(a, "assessments"), "assessments", row)
    s = jget(a, "session")
    if obj(s, "session"):
        arr(jget(s, "emitted_questions"), "session.emitted_questions")
        if jget(s, "emitted_question_ids") is not UNDEF:
            arr(jget(s, "emitted_question_ids"), "session.emitted_question_ids")
    if binding is not None and truthy(binding) and obj(binding, "sourceBinding") and obj(jget(binding, "map"), "sourceBinding.map"):
        arr(jget(jget(binding, "map"), "units"), "sourceBinding.map.units", lambda u, p: obj(u, p))
    return errors


def validate_assessment(a, pkg=None, source_binding=None):
    pkg = pkg or load_package()
    shape = _shape_errors(a, source_binding)
    if shape:
        return {"valid": False, "outcome": "INVALID", "errors": shape, "rows": []}
    errors, rows = [], []

    def err(p, m):
        errors.append(js_str(p) + ": " + m)

    def en(v, values, p):
        if not jin(v, values):
            err(p, "must be one of " + ", ".join(values))

    manifest = pkg["manifest"]
    if not jeq(jget(a, "schema_version"), "1.0.0"):
        err("schema_version", "expected 1.0.0")
    for k in ["bank_sha256", "rubric_sha256"]:
        if not jeq(jget(a, k), jget(manifest, k)):
            err(k, "assessment is not bound to this frozen package")
    evidence = {}  # jkey -> (id, entry)
    ev_list = jget(a, "evidence")
    if not _is_arr(ev_list):
        err("evidence", "must be an array")
    for e in ev_list if _is_arr(ev_list) else []:
        if not is_obj(e):
            err("evidence", "invalid entry")
            continue
        eid = jget(e, "evidence_id")
        if not nonempty(eid) or jkey(eid) in evidence:
            err("evidence", "duplicate or absent evidence_id")
        evidence[jkey(eid)] = e
        for k in ["locator", "exact_excerpt", "actor", "population", "period"]:
            if not nonempty(jget(e, k)):
                err(eid, k + " must be a nonempty string (use unknown explicitly)")
        en(jget(e, "scope"), ["case", "general"], js_str(eid) + ".scope")
        en(jget(e, "temporal"), ["current", "historical", "proposed", "policy", "configured", "unknown"], js_str(eid) + ".temporal")
        en(jget(e, "status"), ["factual", "analytic"], js_str(eid) + ".status")
    source_units = {}
    if source_binding is not None and truthy(source_binding):
        bmap = jget(source_binding, "map")
        if not jeq(jget(a, "source_map_sha256"), jget(source_binding, "sha256")):
            err("source_map_sha256", "assessment must bind to supplied frozen source map")
        units = jget(bmap, "units")
        if not jeq(jget(bmap, "schema_version"), "1.0.0") or not _is_arr(units):
            err("source map", "expected schema_version 1.0.0 and units array")
        for u in units if _is_arr(units) else []:
            loc = jget(u, "locator")
            if not nonempty(loc) or not nonempty(jget(u, "text")) or jkey(loc) in source_units:
                err("source map", "each unit needs unique locator and nonempty text")
            source_units[jkey(loc)] = jget(u, "text")
        for e in evidence.values():
            text = source_units.get(jkey(jget(e, "locator")), UNDEF)
            if not isinstance(text, str):
                err(jget(e, "evidence_id"), "locator absent from frozen source map")
            elif not isinstance(jget(e, "exact_excerpt"), str) or jget(e, "exact_excerpt") not in text:
                err(jget(e, "evidence_id"), "exact_excerpt is not an exact substring at source locator")
    elif jget(a, "source_map_sha256") is not UNDEF:
        err("source map", "assessment declares a source hash but no source map was supplied")

    def refs(lst, p):
        if not _is_arr(lst):
            err(p, "must be an array")
            return []
        if len(set(jkey(x) for x in lst)) != len(lst):
            err(p, "duplicate references")
        for i in lst:
            if jkey(i) not in evidence:
                err(p, "unknown evidence " + js_str(i))
        return [evidence[jkey(i)] for i in lst if jkey(i) in evidence]

    ctx = jget(a, "context")
    if not _is_arr(ctx):
        err("context", "must be an array, separate from credit")
    for i, c in enumerate(ctx if _is_arr(ctx) else []):
        if not is_obj(c):
            err("context[" + str(i) + "]", "invalid entry")
            continue
        refs(jget(c, "evidence_refs"), "context[" + str(i) + "]")
        if not nonempty(jget(c, "note")):
            err("context[" + str(i) + "]", "note required")
    assessments = {}
    alist = jget(a, "assessments")
    if not _is_arr(alist) or len(alist) != 269:
        err("assessments", "exactly 269 rows required, including unresolved rows")
    for q in alist if _is_arr(alist) else []:
        if not is_obj(q):
            err("assessments", "invalid row")
            continue
        qid = jget(q, "question_id")
        if jkey(qid) in assessments:
            err(qid, "duplicate question")
        assessments[jkey(qid)] = (qid, q)
    valid_ids = set(jkey(q["question_id"]) for q in pkg["rubric"]["questions"])
    for k, (qid, _) in assessments.items():
        if k not in valid_ids:
            err(js_str(qid), "unknown question ID")

    for q in pkg["rubric"]["questions"]:
        hit = assessments.get(jkey(q["question_id"]))
        if hit is None:
            err(q["question_id"], "missing assessment")
            continue
        r = hit[1]
        QID = q["question_id"]
        if not jeq(jget(r, "question_text"), q["question_text"]) or not jeq(jget(r, "priority"), q["priority"]):
            err(QID, "exact question text/priority mismatch")
        state = jget(r, "independent_state")
        if not is_obj(state):
            err(QID, "independent_state required; restore applicability, deferral, tracking and conflicts instead of flattening them")
        else:
            ap = jget(state, "applicability")
            if not is_obj(ap):
                err(QID, "applicability object required")
            else:
                en(jget(ap, "status"), ["applicable", "unknown", "not_applicable"], QID + ".applicability")
                ae = refs(jget(ap, "evidence_refs"), QID + ".applicability.evidence_refs")
                if not nonempty(jget(ap, "reason")) or not nonempty(jget(ap, "scope")):
                    err(QID, "applicability reason and scope required")
                if jeq(jget(ap, "status"), "not_applicable") and not any(jeq(jget(e, "status"), "factual") for e in ae):
                    err(QID, "not_applicable requires factual evidence for its scoped premise")
            for flag, reason in [("deferred", "defer_reason"), ("not_tracked", "not_tracked_reason")]:
                if not isinstance(jget(state, flag), bool) or not isinstance(jget(state, reason), str):
                    err(QID, "explicit " + flag + " flag and " + reason + " required")
                if truthy(jget(state, flag)) and not nonempty(jget(state, reason)):
                    err(QID, flag + " requires reason")
            conflicts = jget(state, "conflicts")
            if not _is_arr(conflicts):
                err(QID, "conflicts must be an array")
            cs = set()
            for c in conflicts if _is_arr(conflicts) else []:
                cid = jget(c, "conflict_id")
                if not truthy(c) or not nonempty(cid) or jkey(cid) in cs or not nonempty(jget(c, "note")):
                    err(QID, "conflict needs unique ID and note")
                    continue
                cs.add(jkey(cid))
                if len(refs(jget(c, "evidence_refs"), QID + ".conflict " + js_str(cid))) < 2:
                    err(QID, "conflict must retain at least two evidence references")
        ledger = {}
        frs = jget(r, "facet_results")
        if not _is_arr(frs) or len(frs) != len(q["facets"]):
            err(QID, "exactly the predefined facets required")
        for f in frs if _is_arr(frs) else []:
            if not is_obj(f):
                err(QID, "invalid facet result")
                continue
            fid = jget(f, "facet_id")
            if jkey(fid) in ledger:
                err(QID, "duplicate facet " + js_str(fid))
            ledger[jkey(fid)] = (fid, f)
        fids = set(jkey(f["facet_id"]) for f in q["facets"])
        for k, (fid, _) in ledger.items():
            if k not in fids:
                err(QID, "unknown facet " + js_str(fid))
        positives, gaps = [], []
        for f in q["facets"]:
            p = f["facet_id"]
            hitf = ledger.get(jkey(p))
            if hitf is None:
                err(p, "missing facet result")
                continue
            x = hitf[1]
            en(jget(x, "extent"), ["none", "some", "complete"], p + ".extent")
            en(jget(x, "bounds_result"), ["matched", "unknown", "mismatch"], p + ".bounds_result")
            en(jget(x, "conflict"), ["none", "unresolved"], p + ".conflict")
            if not nonempty(jget(x, "explanation")) or not nonempty(jget(x, "bounds_explanation")):
                err(p, "explanation and bounds_explanation required")
            x_refs = jget(x, "evidence_refs")
            ev = refs(x_refs, p + ".evidence_refs")
            qr = {}
            x_qr = jget(x, "qualifier_results")
            mqs = f["material_qualifiers"]
            if not _is_arr(x_qr) or len(x_qr) != len(mqs):
                err(p, "exact qualifier_results required")
            for z in x_qr if _is_arr(x_qr) else []:
                if not is_obj(z):
                    err(p, "invalid qualifier result")
                    continue
                zid = jget(z, "qualifier_id")
                if jkey(zid) in qr:
                    err(p, "duplicate qualifier")
                qr[jkey(zid)] = (zid, z)
            expected = set(jkey(z["qualifier_id"]) for z in mqs)
            for k, (zid, _) in qr.items():
                if k not in expected:
                    err(p, "unknown qualifier " + js_str(zid))
            extent = jget(x, "extent")
            for z in mqs:
                zid = z["qualifier_id"]
                hitz = qr.get(jkey(zid))
                if hitz is None:
                    err(p, "missing qualifier " + zid)
                    continue
                v = hitz[1]
                vres = jget(v, "result")
                en(vres, ["supported", "unknown", "contradicted"], zid)
                v_refs = jget(v, "evidence_refs")
                ze = refs(v_refs, zid + ".evidence_refs")
                if not nonempty(jget(v, "basis")):
                    err(zid, "basis required")
                if jeq(vres, "supported"):
                    kind = jget(z, "kind")
                    if not ze:
                        err(zid, "supported qualifier requires evidence")
                    if _is_arr(v_refs) and any((not _is_arr(x_refs)) or not jin(i, x_refs) for i in v_refs):
                        err(zid, "qualifier evidence must also be in facet evidence_refs")
                    if jin(kind, ["current", "active", "unused"]) and not any(jeq(jget(e, "temporal"), "current") for e in ze):
                        err(zid, "requires current evidence, not only historical/configured/proposed")
                    if jin(kind, ["usual", "pattern", "rank", "all"]) and not (jeq(kind, "all") and truthy(jget(z, "partial_population_allowed")) and jeq(extent, "some") and jeq(jget(f, "scope_policy"), "general_for_complete")) and not any(jeq(jget(e, "scope"), "general") for e in ze):
                        err(zid, "requires general/representative evidence, not isolated case")
                    if jeq(kind, "attributed_wish") and ((not ze) or any(not jeq(jget(e, "status"), "factual") for e in ze)):
                        err(zid, "assigned agent wish requires factual attributed evidence, not analytic advice")
                    if jeq(kind, "first") and not jin(jget(v, "basis"), ["explicit_first", "complete_chronology"]):
                        err(zid, "basis must be explicit_first or complete_chronology; an occurrence alone is insufficient")
                if not jeq(extent, "none") and not jeq(vres, "supported"):
                    err(zid, "positive extent cannot coexist with " + js_str(vres) + " material qualifier")
            if truthy(jget(f, "component_scope_required")):
                en(jget(x, "component_scope"), ["unknown", "subset", "all_applicable"], p + ".component_scope")
                if not nonempty(jget(x, "component_scope_basis")):
                    err(p, "component_scope_basis required")
                cse = jget(x, "component_scope_evidence_refs")
                scope_ev = refs(cse, p + ".component_scope_evidence_refs")
                if _is_arr(cse) and any(not jin(i, x_refs) for i in cse):
                    err(p, "component-scope evidence must also be in facet evidence_refs")
                if not jeq(extent, "none") and not any(jeq(jget(e, "status"), "factual") for e in scope_ev):
                    err(p, "positive paperwork scope requires factual component-scope evidence")
                if jeq(extent, "some") and not jeq(jget(x, "component_scope"), "subset"):
                    err(p, "some requires a supported nonempty paperwork subset")
                if jeq(extent, "complete") and not jeq(jget(x, "component_scope"), "all_applicable"):
                    err(p, "complete requires all applicable disclosures and agreements within the stated scope")
            role_answer = jeq(jget(f, "scope_evidence_role"), "answer_evidence_refs")
            aer = jget(x, "answer_evidence_refs")
            answer_ev = refs(aer, p + ".answer_evidence_refs") if role_answer else ev
            if role_answer and _is_arr(aer) and any(not jin(i, x_refs) for i in aer):
                err(p, "answer evidence must also be in facet evidence_refs")
            if not jeq(extent, "none"):
                for dep in jget(f, "requires_supported_facets") if _is_arr(jget(f, "requires_supported_facets")) else []:
                    dhit = ledger.get(jkey(dep))
                    dr = dhit[1] if dhit else None
                    if not dr or not jin(jget(dr, "extent"), ["some", "complete"]):
                        err(p, "positive extent requires supported referent facet " + js_str(dep))
                    elif not any(jin(i, x_refs) for i in jget(dr, "evidence_refs")):
                        err(p, "dependent reason must retain ranking evidence from " + js_str(dep))
                if role_answer and not any(jeq(jget(e, "status"), "factual") for e in answer_ev):
                    err(p, "positive reason requires separate factual answer_evidence_refs")
                if not ev:
                    err(p, "positive extent requires evidence")
                if jeq(extent, "some") and not truthy(jget(f, "allows_some")):
                    err(p, "some is not permitted for this indivisible proposition")
                if not jeq(jget(x, "bounds_result"), "matched"):
                    err(p, "positive extent requires matched bounds")
                if not jeq(jget(x, "conflict"), "none"):
                    err(p, "positive extent cannot carry unresolved conflict")
                if not any(jeq(jget(e, "status"), "factual") for e in ev):
                    err(p, "positive extent requires factual evidence or factual premises; analysis alone cannot satisfy it")
                if jeq(jget(f, "mode"), "factual") and all(jeq(jget(e, "status"), "analytic") for e in ev):
                    err(p, "analysis-only evidence cannot satisfy factual facet")
                if jeq(jget(f, "scope_policy"), "general_required") and not any(jeq(jget(e, "scope"), "general") for e in ev):
                    err(p, "general evidence required")
                if jeq(jget(f, "scope_policy"), "general_for_complete") and jeq(extent, "complete") and not any(jeq(jget(e, "scope"), "general") for e in answer_ev):
                    err(p, "complete requires general scope; a true case method can be some")
                if jeq(jget(f, "mode"), "factual") and all(jin(jget(e, "temporal"), ["proposed", "unknown"]) for e in ev):
                    err(p, "proposed/unknown-only evidence does not establish factual practice")
                pos = {"facet_id": p, "extent": extent, "proposition": f["proposition"], "evidence_refs": x_refs, "scope": unique([jget(e, "scope") for e in ev])}
                if truthy(jget(f, "component_scope_required")):
                    pos["component_scope"] = jget(x, "component_scope")
                    pos["component_scope_basis"] = jget(x, "component_scope_basis")
                    pos["component_scope_evidence_refs"] = jget(x, "component_scope_evidence_refs")
                positives.append(pos)
            missing = jget(x, "missing")
            if not _is_arr(missing):
                err(p, "structured missing array required")
            else:
                for m in missing:
                    if not is_obj(m):
                        err(p, "missing entry must be an object")
                        continue
                    if not jin(jget(m, "code"), MISSING_CODES):
                        err(p, "unknown missing code " + js_str(jget(m, "code")))
                    keys = list(m.keys()) if isinstance(m, dict) else [str(i) for i in range(len(m))]
                    if any(k not in ("code", "qualifier_id") for k in keys):
                        err(p, "unsupported missing field")
                required = expected_missing(x)
                if _canonical_missing(missing) != _canonical_missing(required):
                    err(p, "missing ledger must equal derived codes " + stringify(required))
            for m in expected_missing(x):
                g = {"facet_id": p, "proposition": f["proposition"]}
                g.update(m)
                gaps.append(g)
        complete = all(jeq(jget(ledger[jkey(f["facet_id"])][1], "extent") if jkey(f["facet_id"]) in ledger else UNDEF, "complete") for f in q["facets"] if truthy(f.get("required_for_full")))
        label = "fully_answered" if complete else ("partially_answered" if positives else "unresolved")
        if jget(r, "label") is not UNDEF and not jeq(jget(r, "label"), label):
            err(QID, "supplied label disagrees; derived " + label)
        if jget(r, "positive_summary") is not UNDEF and not same(jget(r, "positive_summary"), positives):
            err(QID, "positive_summary disagrees with derived ledger")
        if jget(r, "missing_summary") is not UNDEF and not same(jget(r, "missing_summary"), gaps):
            err(QID, "missing_summary disagrees with derived ledger")
        has_conflict = any(jeq(jget(fv, "conflict"), "unresolved") for (_, fv) in ledger.values())
        st_conf = jget(state, "conflicts") if is_obj(state) else UNDEF
        if has_conflict and not (isinstance(st_conf, (list, str)) and len(st_conf) > 0):
            err(QID, "unresolved facet conflict requires preserved conflict history in independent_state")
        ap_status = jget(jget(state, "applicability"), "status") if is_obj(state) else UNDEF
        if jeq(ap_status, "not_applicable"):
            suppression = "supported_not_applicable"
        elif is_obj(state) and truthy(jget(state, "deferred")):
            suppression = "deferred"
        elif is_obj(state) and truthy(jget(state, "not_tracked")):
            suppression = "not_tracked_retrieve_or_defer"
        elif label == "fully_answered":
            suppression = "already_answered"
        else:
            suppression = None
        rows.append({"question_id": QID, "label": label, "independent_state": state,
                     "question_gate": {"eligible_for_gap_selection": suppression is None, "suppression_reason": suppression, "authorization": "Eligibility is not permission: apply session stop, budget and one-question rules separately."},
                     "positive_summary": positives, "missing_summary": gaps})

    s = jget(a, "session")
    if not is_obj(s):
        err("session", "session record required")
    else:
        en(jget(s, "status"), ["active", "paused", "stopped", "complete"], "session.status")
        command = normalize_command(jget(s, "command"))
        if not command:
            err("session.command", "unknown documented command")
        if command == "deepen" and (not jeq(jget(s, "pass"), 2) or not truthy(jget(s, "deepen_authorized")) or truthy(jget(s, "pass2_declined"))):
            err("session", "Deepen discovery requires explicit authorized nondeclined Pass 2")
        sa = jget(s, "substantive_answers")
        if not isinstance(jget(s, "timing_reliable"), bool) or not is_integer(sa) or js_lt(sa, 0):
            err("session", "valid timing reliability and answer counter required")
        if not jin(jget(s, "pass"), [1, 2]) or not isinstance(jget(s, "deepen_authorized"), bool) or not isinstance(jget(s, "pass2_declined"), bool):
            err("session", "valid pass and depth decisions required")
        bm = jget(s, "budget_minutes")
        if not is_finite(bm) or js_le(bm, 0):
            err("session", "positive budget required")
        am = jget(s, "active_minutes")
        if truthy(jget(s, "timing_reliable")) and (not is_finite(am) or js_lt(am, 0)):
            err("session", "reliable timing requires active_minutes")
        eq = jget(s, "emitted_questions")
        if not _is_arr(eq) or any(not nonempty(x) for x in eq):
            err("session", "emitted_questions must be string array")
        if not isinstance(jget(s, "exported"), bool):
            err("session", "exported boolean required")
        normalized = normalize_command(jget(s, "command"))
        output_only = normalized not in ("discovery", "start_quick_discovery", "resume", "deepen")
        export_command = normalized in ("snapshot", "pause", "stop", "final_report")
        exhausted = jeq(jget(s, "pass"), 1) and (js_ge(am, bm) if truthy(jget(s, "timing_reliable")) else js_ge(sa, 6))
        status_stop = jin(jget(s, "status"), ["paused", "stopped", "complete"])
        stopped = status_stop or output_only or exhausted
        eq_list = eq if truthy(eq) else []
        n_eq = len(eq_list) if isinstance(eq_list, (list, str)) else 0
        if stopped and n_eq:
            err("session", "stop/output-only/budget exhaustion forbids new questions")
        if (status_stop or export_command or exhausted) and not truthy(jget(s, "exported")):
            err("session", "stop/output-only/budget exhaustion requires qualified export")
        if jeq(jget(s, "pass"), 2) and (not truthy(jget(s, "deepen_authorized")) or truthy(jget(s, "pass2_declined"))):
            err("session", "Pass 2 requires explicit nondeclined authorization")
        if n_eq:
            eqi = jget(s, "emitted_question_ids")
            if not _is_arr(eqi) or len(eqi) != n_eq:
                err("session", "each emitted question needs an emitted_question_ids entry for the independent-state gate")
            else:
                for qid in eqi:
                    row = next((rr for rr in rows if jeq(rr["question_id"], qid)), None)
                    if row is None:
                        err("session", "unknown emitted question ID " + js_str(qid))
                    elif not row["question_gate"]["eligible_for_gap_selection"]:
                        err("session", "question selection blocked for " + js_str(qid) + ": " + js_str(row["question_gate"]["suppression_reason"]))
        if n_eq > 1:
            err("session", "one natural question maximum per interaction")
    if errors:
        return {"valid": False, "outcome": "INVALID", "errors": errors, "rows": []}
    counts = {"fully_answered": 0, "partially_answered": 0, "unresolved": 0}
    for rr in rows:
        counts[rr["label"]] += 1
    return {"valid": True, "outcome": "VALID", "normalized_command": normalize_command(a["session"]["command"]),
            "validation_scope": "Structural consistency only; semantic entailment and destination execution are not proven.",
            "excerpt_verification": "Exact substrings and locators checked against supplied frozen source map" if (source_binding is not None and truthy(source_binding)) else "Unverified: no frozen source map supplied",
            "bank_sha256": manifest["bank_sha256"], "rubric_sha256": manifest["rubric_sha256"], "errors": [],
            "independent_state_counts": {"not_applicable": sum(1 for rr in rows if jeq(rr["independent_state"]["applicability"]["status"], "not_applicable")),
                                         "deferred": sum(1 for rr in rows if truthy(rr["independent_state"]["deferred"])),
                                         "not_tracked": sum(1 for rr in rows if truthy(rr["independent_state"]["not_tracked"])),
                                         "conflicted": sum(1 for rr in rows if len(rr["independent_state"]["conflicts"]) > 0)},
            "counts": counts, "rows": rows}


# --------------------------------------------------------------------------- CLI


def _write_new(path, text):
    with open(path, "x", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    pkg_dir = None
    if "--dir" in args:
        i = args.index("--dir")
        if i + 1 >= len(args):
            print("INVALID: --dir requires a folder path", file=sys.stderr)
            return 2
        pkg_dir = args[i + 1]
        del args[i:i + 2]
    try:
        pkg = load_package(pkg_dir)
        if args and args[0] == "--check-package":
            facets = sum(len(q["facets"]) for q in pkg["rubric"]["questions"])
            print(stringify({"valid": True, "questions": 269, "facets": facets, "bank_sha256": pkg["manifest"]["bank_sha256"], "rubric_sha256": pkg["manifest"]["rubric_sha256"]}, 2))
            return 0
        if args and args[0] == "--template":
            text = stringify(blank_assessment(pkg), 2) + "\n"
            if len(args) > 1:
                _write_new(args[1], text)
            else:
                sys.stdout.write(text)
            return 0
        if args:
            binding = None
            if "--sources" in args:
                si = args.index("--sources")
                if si + 1 >= len(args):
                    raise RuntimeError("--sources requires a JSON source-map path")
                with open(args[si + 1], "rb") as fh:
                    b = fh.read()
                binding = {"map": parse_json_bytes(b), "sha256": sha256(b)}
            out = validate_assessment(parse(args[0]), pkg, binding)
            text = stringify(out, 2) + "\n"
            if len(args) > 1 and args[1] != "--sources":
                _write_new(args[1], text)
            else:
                sys.stdout.write(text)
            return 0 if out["valid"] else 1
        print("Usage: python validate_coverage.py --check-package | --template [new.json] | assessment.json [new-result.json] [--sources source-map.json] [--dir folder]", file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001 - CLI boundary, mirrors the JS catch-all
        print("INVALID: " + str(e), file=sys.stderr)
        return 2


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    except Exception:  # noqa: BLE001
        pass
    sys.exit(main())
