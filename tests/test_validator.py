"""Python port of the inherited JavaScript suites (48 + 21 + 44 + 25 = 138 checks)."""
import copy
import unittest

from _helpers import PKG, facet, fresh, row, validate, vc

EM = vc.expected_missing


# ---------------------------------------------------------------- test-validation.mjs (48)
def evidence(a, **over):
    n = len(a["evidence"]) + 1
    e = {"evidence_id": "E%d" % n, "locator": "anonymous-source.txt#paragraph-%d" % n,
         "exact_excerpt": "For this buyer I counted available calendar slots to measure capacity.",
         "scope": "case", "temporal": "current", "status": "factual", "actor": "assigned coordinator",
         "population": "one anonymous buyer", "period": "assessment date"}
    e.update(over)
    a["evidence"].append(e)
    return e["evidence_id"]


def credit(a, qid, refs, extent="some", i=0):
    f = facet(a, qid, i)
    f["extent"] = extent
    f["evidence_refs"] = list(refs)
    f["bounds_result"] = "matched"
    f["bounds_explanation"] = "Reviewer declares the evidence matches the exact requested actor, event, population, time and unit."
    f["explanation"] = "The cited source supplies the requested answer at its explicitly stated scope."
    for z in f["qualifier_results"]:
        z["result"] = "supported"
        z["evidence_refs"] = list(refs)
        z["basis"] = "explicit_first" if z["qualifier_id"].endswith(".first") else "Explicit support for the credited component"
    f["missing"] = EM(f)
    return f


class Suite48(unittest.TestCase):
    def check(self, a, valid, contains=None, label=None, qid=None):
        r = validate(a)
        self.assertEqual(r["valid"], valid, r["errors"][:5])
        if contains:
            self.assertTrue(any(contains in e for e in r["errors"]), (contains, r["errors"][:5]))
        if label:
            self.assertEqual(next(x for x in r["rows"] if x["question_id"] == qid)["label"], label)
        return r

    def test_01_valid_stopped_unknown_export(self): self.check(fresh(), True)

    def test_02_case_method_partial(self):
        a = fresh(); credit(a, "Q13.14", [evidence(a)]); self.check(a, True, qid="Q13.14", label="partially_answered")

    def test_03_capacity_value_no_method(self):
        a = fresh(); e = evidence(a, exact_excerpt="There were three free slots.")
        a["context"] = [{"evidence_refs": [e], "note": "A capacity value does not establish a measurement method."}]
        self.check(a, True, qid="Q13.14", label="unresolved")

    def test_04_case_not_general_complete(self):
        a = fresh(); credit(a, "Q13.14", [evidence(a)], "complete"); self.check(a, False, contains="complete requires general")

    def test_05_general_method_complete(self):
        a = fresh(); e = evidence(a, scope="general", population="team practice", exact_excerpt="We measure available capacity by counting each assigned person’s open calendar slots.")
        credit(a, "Q13.14", [e], "complete"); self.check(a, True, qid="Q13.14", label="fully_answered")

    def test_06_case_not_usual(self):
        a = fresh(); credit(a, "Q09.02", [evidence(a, exact_excerpt="For this buyer appointment 2 was booked the next day.")]); self.check(a, False, contains="requires general")

    def test_07_general_habit_usual(self):
        a = fresh(); credit(a, "Q09.02", [evidence(a, scope="general", exact_excerpt="We usually schedule appointment 2 on the next business day.")], "complete")
        self.check(a, True, qid="Q09.02", label="fully_answered")

    def test_08_historical_not_current(self):
        a = fresh(); credit(a, "Q14.13", [evidence(a, scope="general", temporal="historical", exact_excerpt="Last quarter some pipeline totals were inaccurate.")], "complete")
        self.check(a, False, contains="requires current")

    def test_09_current_inaccuracy(self):
        a = fresh(); credit(a, "Q14.13", [evidence(a, scope="general", exact_excerpt="As of today the current pipeline total is known to double-count three leads.")], "complete")
        self.check(a, True, qid="Q14.13", label="fully_answered")

    def test_10_occurrence_not_first(self):
        a = fresh(); f = credit(a, "Q08.01", [evidence(a, exact_excerpt="Financing was discussed at the first appointment.")], "complete")
        f["qualifier_results"][0]["result"] = "unknown"; f["qualifier_results"][0]["basis"] = "An occurrence, not first occurrence"; f["missing"] = EM(f)
        self.check(a, False, contains="unknown material qualifier")

    def test_11_explicit_first(self):
        a = fresh(); credit(a, "Q08.01", [evidence(a, exact_excerpt="The first time financing was discussed with this buyer was during appointment 1.")], "complete")
        self.check(a, True, qid="Q08.01", label="fully_answered")

    def test_12_complete_chronology(self):
        a = fresh(); f = credit(a, "Q08.01", [evidence(a, exact_excerpt="The complete communication record from inquiry through meeting contains no financing discussion before the appointment 1 discussion.")], "complete")
        f["qualifier_results"][0]["basis"] = "complete_chronology"; self.check(a, True)

    def test_13_actor_identification(self):
        a = fresh(); credit(a, "Q10.32", [evidence(a, exact_excerpt="The assigned showing agent selects or approves the initial property list.", actor="showing agent")], "complete")
        self.check(a, True, qid="Q10.32", label="fully_answered")

    def test_14_analysis_not_factual_owner(self):
        a = fresh(); credit(a, "Q10.32", [evidence(a, status="analytic", exact_excerpt="I infer that the showing agent probably selects the list.")], "complete")
        self.check(a, False, contains="requires factual")

    def test_15_labeled_limited_evaluation(self):
        a = fresh(); e = evidence(a, exact_excerpt="Buyers ask what the lender range means before appointment 2.")
        i = evidence(a, status="analytic", exact_excerpt="Limited inference: understanding lender range before appointment 2 would prepare buyers for that discussion.")
        credit(a, "Q09.14", [e, i]); self.check(a, True, qid="Q09.14", label="partially_answered")

    def test_16_positive_label_unknown_qualifier(self):
        a = fresh(); f = credit(a, "Q09.02", [evidence(a, scope="general")]); f["qualifier_results"][0]["result"] = "unknown"; f["missing"] = EM(f)
        row(a, "Q09.02")["label"] = "partially_answered"; self.check(a, False, contains="unknown material qualifier")

    def test_17_invalid_question_id(self):
        a = fresh(); a["assessments"][0]["question_id"] = "Q99.99"; self.check(a, False, contains="unknown question ID")

    def test_18_missing_facet(self):
        a = fresh(); a["assessments"][0]["facet_results"].pop(); self.check(a, False, contains="predefined facets")

    def test_19_bad_evidence_reference(self):
        a = fresh(); credit(a, "Q10.32", ["missing"], "complete"); self.check(a, False, contains="unknown evidence")

    def test_20_supplied_label_mismatch(self):
        a = fresh(); a["assessments"][0]["label"] = "fully_answered"; self.check(a, False, contains="supplied label disagrees")

    def test_21_wrong_frozen_rubric(self):
        a = fresh(); a["rubric_sha256"] = "changed"; self.check(a, False, contains="not bound")

    def test_22_changed_question_text(self):
        a = fresh(); a["assessments"][0]["question_text"] += " changed"; self.check(a, False, contains="text/priority mismatch")

    def test_23_invalid_missing_code(self):
        a = fresh(); a["assessments"][0]["facet_results"][0]["missing"].append({"code": "invented"}); self.check(a, False, contains="unknown missing code")

    def test_24_six_answer_auto_export(self):
        a = fresh(); a["session"].update(command="discovery", status="active", substantive_answers=6); self.check(a, True)

    def test_25_stopped_export_forbids_question(self):
        a = fresh(); a["session"].update(substantive_answers=6, emitted_questions=["One more question?"]); self.check(a, False, contains="forbids new questions")

    def test_26_positive_unknown_bounds(self):
        a = fresh(); f = credit(a, "Q13.14", [evidence(a)]); f["bounds_result"] = "unknown"; f["missing"] = EM(f); self.check(a, False, contains="requires matched bounds")

    def test_27_positive_unresolved_conflict(self):
        a = fresh(); f = credit(a, "Q13.14", [evidence(a)]); f["conflict"] = "unresolved"; f["missing"] = EM(f); self.check(a, False, contains="unresolved conflict")

    def test_28_disallowed_some(self):
        a = fresh(); credit(a, "Q10.32", [evidence(a)], "some"); self.check(a, False, contains="some is not permitted")

    def test_29_complete_with_missing_component(self):
        a = fresh(); f = credit(a, "Q13.14", [evidence(a, scope="general")], "complete"); f["missing"] = [{"code": "incomplete_component"}]; self.check(a, False, contains="missing ledger")

    def test_30_invalid_qualifier_id(self):
        a = fresh(); facet(a, "Q09.02")["qualifier_results"][0]["qualifier_id"] = "invented"; self.check(a, False, contains="unknown qualifier")

    def test_31_inconsistent_positive_summary(self):
        a = fresh(); credit(a, "Q08.01", [evidence(a)], "complete"); row(a, "Q08.01")["positive_summary"] = []; self.check(a, False, contains="positive_summary disagrees")

    def test_32_inconsistent_missing_summary(self):
        a = fresh(); a["assessments"][0]["missing_summary"] = []; self.check(a, False, contains="missing_summary disagrees")

    def test_33_bounded_reviewable_availability(self):
        a = fresh(); e = evidence(a, scope="general", exact_excerpt="Only March paid-social records can be reviewed reliably; other periods and sources are unavailable.")
        credit(a, "Q15.01", [e], "complete", 0); credit(a, "Q15.01", [e], "complete", 1); self.check(a, True, qid="Q15.01", label="fully_answered")

    def test_34_LIMIT_false_first_support(self):
        a = fresh(); credit(a, "Q08.01", [evidence(a, exact_excerpt="Financing came up during appointment 1.")], "complete"); self.check(a, True)

    def test_35_LIMIT_false_current_inaccuracy(self):
        a = fresh(); credit(a, "Q14.13", [evidence(a, scope="general", exact_excerpt="A status update was delayed last year.")], "complete"); self.check(a, True)

    def test_36_independent_compound_partial(self):
        a = fresh(); credit(a, "Q06.01", [evidence(a, scope="general", exact_excerpt="We usually use a shared calendar to assign appointment 1 conductors.")], "complete", 1)
        self.check(a, True, qid="Q06.01", label="partially_answered")

    def test_37_39_source_bound(self):
        a = fresh(); credit(a, "Q13.14", [evidence(a, exact_excerpt="The coordinator measures available capacity by counting open calendar slots.")])
        m = {"schema_version": "1.0.0", "units": [{"locator": a["evidence"][0]["locator"], "text": "Record start. " + a["evidence"][0]["exact_excerpt"] + " Record end."}]}
        b = {"map": m, "sha256": vc.sha256(vc.stringify(m, 2) + "\n")}
        a["source_map_sha256"] = b["sha256"]
        self.assertTrue(validate(a, b)["valid"])
        a["evidence"][0]["exact_excerpt"] = "Invented quotation not in source"
        r = validate(a, b); self.assertFalse(r["valid"]); self.assertTrue(any("exact substring" in e for e in r["errors"]))
        a["source_map_sha256"] = "wrong"; self.assertFalse(validate(a, b)["valid"])

    def test_40_supported_na_preserved(self):
        a = fresh(); e = evidence(a, scope="general", exact_excerpt="There is no appointment 2 in our current buyer process.")
        r = row(a, "Q09.03"); r["independent_state"]["applicability"] = {"status": "not_applicable", "evidence_refs": [e], "reason": "No inter-appointment interval exists because appointment 2 is not part of this scoped process.", "scope": "Current team buyer process"}
        out = self.check(a, True, qid="Q09.03", label="unresolved")
        o = next(x for x in out["rows"] if x["question_id"] == "Q09.03")
        self.assertEqual(o["independent_state"], r["independent_state"]); self.assertFalse(o["question_gate"]["eligible_for_gap_selection"])

    def test_41_unsupported_na_rejected(self):
        a = fresh(); a["assessments"][0]["independent_state"]["applicability"]["status"] = "not_applicable"; self.check(a, False, contains="requires factual evidence")

    def test_42_supported_na_cannot_be_reasked(self):
        a = fresh(); e = evidence(a, scope="general", exact_excerpt="There is no appointment 2 in this process.")
        row(a, "Q09.03")["independent_state"]["applicability"] = {"status": "not_applicable", "evidence_refs": [e], "reason": "No interval", "scope": "Current team"}
        a["session"].update(status="active", command="discovery", emitted_questions=["Who owns the interval?"], emitted_question_ids=["Q09.03"])
        self.check(a, False, contains="question selection blocked")

    def test_43_deferred_not_tracked_preserved(self):
        a = fresh(); r = row(a, "Q15.02"); s = r["independent_state"]
        s.update(deferred=True, defer_reason="Owner deferred until a report is available", not_tracked=True, not_tracked_reason="Unique source-cohort counts are not tracked")
        out = self.check(a, True); o = next(x for x in out["rows"] if x["question_id"] == "Q15.02")
        self.assertEqual(o["independent_state"], s); self.assertFalse(o["question_gate"]["eligible_for_gap_selection"])

    def test_44_unresolved_conflict_preserved(self):
        a = fresh(); e1 = evidence(a, exact_excerpt="Person A owns tour scheduling."); e2 = evidence(a, exact_excerpt="Person B owns tour scheduling.")
        f = facet(a, "Q11.07", 1); f["conflict"] = "unresolved"; f["evidence_refs"] = [e1, e2]; f["missing"] = EM(f)
        row(a, "Q11.07")["independent_state"]["conflicts"] = [{"conflict_id": "C1", "evidence_refs": [e1, e2], "note": "Competing owner accounts; neither superseded"}]
        self.check(a, True)

    def test_45_negative_handoff(self):
        a = fresh(); e = evidence(a, scope="general", exact_excerpt="We do not hand buyers off between agents.")
        credit(a, "Q11.13", [e], "complete", 0); credit(a, "Q11.13", [e], "complete", 1)
        out = self.check(a, True, qid="Q11.13", label="fully_answered")
        self.assertEqual(next(x for x in out["rows"] if x["question_id"] == "Q11.13")["missing_summary"], [])

    def test_46_negative_discussion(self):
        a = fresh(); e = evidence(a, scope="general", exact_excerpt="At appointment 1 we do not discuss compensation, representation agreements, services, duration or termination.")
        for i in range(5):
            credit(a, "Q07.14", [e], "complete", i)
        out = self.check(a, True, qid="Q07.14", label="fully_answered")
        self.assertEqual(next(x for x in out["rows"] if x["question_id"] == "Q07.14")["missing_summary"], [])

    def test_47_tracking_answered_no(self):
        a = fresh(); credit(a, "Q15.18", [evidence(a, scope="general", exact_excerpt="We do not measure retained contribution after compensation splits and variable costs.")], "complete")
        row(a, "Q15.18")["independent_state"].update(not_tracked=True, not_tracked_reason="Explicitly not measured")
        self.check(a, True, qid="Q15.18", label="fully_answered")

    def test_48_conflict_history_required(self):
        a = fresh(); f = facet(a, "Q11.08"); f["conflict"] = "unresolved"; f["missing"] = EM(f); self.check(a, False, contains="requires preserved conflict history")


# ---------------------------------------------------------------- test-d1.mjs (21)
def ev_d1(a, text, actor):
    i = "E%d" % (len(a["evidence"]) + 1)
    a["evidence"].append({"evidence_id": i, "locator": "anonymous#" + i, "exact_excerpt": text, "scope": "case", "temporal": "current", "status": "factual", "actor": actor, "population": "one buyer within explicitly stated service/tour scope", "period": "current"})
    return i


def support(a, qid, refs, extent="complete"):
    f = facet(a, qid)
    f.update(extent=extent, evidence_refs=list(refs), bounds_result="matched", bounds_explanation="Correct actor, event and declared scope", explanation="The requested actor/action is stated within the source scope")
    for z in f["qualifier_results"]:
        z.update(result="supported", evidence_refs=list(refs), basis="explicit_first" if z["qualifier_id"].endswith(".first") else "Explicit stated support")
    f["missing"] = EM(f)
    return f


def paperwork(text, scope="subset", extent="some"):
    a = fresh(); e = ev_d1(a, text, "named verifier"); f = support(a, "Q11.04", [e], extent)
    f.update(component_scope=scope, component_scope_basis=("Only the identified agreement is established; other applicable paperwork remains unknown." if scope == "subset" else "All applicable paperwork in this specified service/tour scope is covered."), component_scope_evidence_refs=[e])
    return a


class SuiteD1(unittest.TestCase):
    def check(self, a, want, label=None):
        r = validate(a); self.assertEqual(r["valid"], want, r["errors"][:5])
        if label:
            self.assertEqual(next(x for x in r["rows"] if x["question_id"] == "Q11.04")["label"], label)
        return r

    def test_roles(self):
        for qid in ["Q03.04", "Q13.08"]:
            q = next(q for q in PKG["rubric"]["questions"] if q["question_id"] == qid)
            b = q["facets"][0]["bounds"]["actor"]; self.assertIn("VA", b); self.assertIn("agent", b)
            ext = "some" if qid == "Q13.08" else "complete"
            for role in ["agent", "VA"]:
                a = fresh(); text = ("The assigned %s was responsible for the first contact with this buyer." if qid == "Q03.04" else "The assigned %s was absent, so the named backup covered this buyer.") % role
                support(a, qid, [ev_d1(a, text, role)], ext); self.check(a, True)
            a = fresh(); f = support(a, qid, [ev_d1(a, "The assignee handled this buyer; their role is unknown.", "unknown")], ext)
            next(z for z in f["qualifier_results"] if z["qualifier_id"].endswith(".role"))["result"] = "unknown"; f["missing"] = EM(f); self.check(a, False)
            a = fresh(); f = support(a, qid, [ev_d1(a, "An unrelated agent acted on a different event.", "agent")], ext)
            f["bounds_result"] = "mismatch"; f["missing"] = EM(f); self.check(a, False)

    def test_paperwork(self):
        self.check(paperwork("The coordinator verifies this required agreement is complete before the tour. Other required paperwork is not described."), True, "partially_answered")
        self.check(paperwork("The coordinator verifies this required disclosure is complete before the applicable service. Other required paperwork is not described."), True, "partially_answered")
        self.check(paperwork("Only one agreement verifier is established before the tour.", "subset", "complete"), False)
        r = self.check(paperwork("The coordinator verifies completion of all disclosures and agreements applicable to this buyer before the services or tours requiring them.", "all_applicable", "complete"), True, "fully_answered")
        self.assertEqual(next(x for x in r["rows"] if x["question_id"] == "Q11.04")["positive_summary"][0]["component_scope"], "all_applicable")
        self.check(paperwork("For this explicitly bounded service, the only applicable required paperwork is this agreement. The coordinator verifies its completion before that service; no disclosures are applicable.", "all_applicable", "complete"), True, "fully_answered")
        for ext in ["some", "complete"]:
            a = paperwork("The coordinator verifies paperwork but timing is unknown.", "subset" if ext == "some" else "all_applicable", ext)
            f = facet(a, "Q11.04"); f["qualifier_results"][0].update(result="unknown", basis="Before-event timing not established"); f["missing"] = EM(f); self.check(a, False)
        a = paperwork("The coordinator checks the agreement after the relevant service."); f = facet(a, "Q11.04"); f["qualifier_results"][0]["result"] = "contradicted"; f["missing"] = EM(f); self.check(a, False)
        a = paperwork("Paperwork was checked before a later unrelated meeting, not the applicable tour."); f = facet(a, "Q11.04"); f["bounds_result"] = "mismatch"; f["missing"] = EM(f); self.check(a, False)
        self.check(paperwork("A person was named but their paperwork scope was not established.", "unknown"), False)
        a = paperwork("Subset checker before tour."); del facet(a, "Q11.04")["component_scope"]; self.check(a, False)
        a = paperwork("Subset checker before tour."); facet(a, "Q11.04")["component_scope_evidence_refs"] = []; self.check(a, False)
        a = fresh(); a["rubric_sha256"] = "frozen-D-hash"; self.check(a, False)


# ---------------------------------------------------------------- review-fix-regressions.mjs (44)
def ev_r(a, text, **extra):
    i = "E%d" % (len(a["evidence"]) + 1)
    e = {"evidence_id": i, "locator": "anonymous#" + i, "exact_excerpt": text, "scope": "general", "temporal": "current", "status": "factual", "actor": "assigned agent", "population": "team buyers", "period": "current"}
    e.update(extra); a["evidence"].append(e); return i


def credit_r(a, qid, refs, extent="complete", i=0):
    x = facet(a, qid, i)
    x.update(extent=extent, evidence_refs=list(refs), bounds_result="matched", bounds_explanation="Matches declared question actor, event and scope", explanation="Anonymous source answers the requested proposition")
    for z in x["qualifier_results"]:
        z.update(result="supported", evidence_refs=list(refs), basis="Explicit factual support")
    x["missing"] = EM(x)
    return x


class SuiteReviewFix(unittest.TestCase):
    def check(self, a, want):
        r = validate(a); self.assertEqual(r["valid"], want, r["errors"][:5]); return r

    def test_semantics(self):
        a = fresh(); e = ev_r(a, "This buyer entered our active Meta campaign today.", scope="case"); credit_r(a, "Q02.01", [e], "some"); self.check(a, True); credit_r(a, "Q02.01", [e], "complete"); self.check(a, False)
        a = fresh(); x = credit_r(a, "Q02.01", [ev_r(a, "This buyer entered a campaign.", scope="case")], "some")
        next(z for z in x["qualifier_results"] if z["qualifier_id"].endswith(".active"))["result"] = "unknown"; x["missing"] = EM(x); self.check(a, False)
        a = fresh(); credit_r(a, "Q01.06", [ev_r(a, "One buyer asked a question.", scope="case")], "some"); self.check(a, False)
        a = fresh(); credit_r(a, "Q06.11", [ev_r(a, "The assigned agent wishes prospects understood purchase costs before appointment 1.")]); self.check(a, True)
        a = fresh(); e = ev_r(a, "Buyers ask about costs."); i = ev_r(a, "Inference: the agent would ideally want costs understood beforehand.", status="analytic"); credit_r(a, "Q06.11", [e, i]); self.check(a, False)
        a = fresh(); e = ev_r(a, "One buyer rejected Market B due to commute.", scope="case"); x = credit_r(a, "Q10.20", [e], "some", 1); x["answer_evidence_refs"] = [e]; self.check(a, False)
        a = fresh(); rank = ev_r(a, "Market B is the most frequently rejected alternative in our team records."); reason = ev_r(a, "This buyer rejected Market B because of commute.", scope="case")
        credit_r(a, "Q10.20", [rank], "complete", 0); x = credit_r(a, "Q10.20", [rank, reason], "some", 1); x["answer_evidence_refs"] = [reason]; self.check(a, True)
        x["extent"] = "complete"; x["missing"] = EM(x); self.check(a, False)
        a = fresh(); e = ev_r(a, "Prospects can easily access materials on their preferred device and in their preferred language."); credit_r(a, "Q16.10", [e], "complete", 0); x = credit_r(a, "Q16.10", [e], "complete", 1); self.check(a, True)
        x["qualifier_results"][0]["result"] = "unknown"; x["missing"] = EM(x); self.check(a, False)

    def test_commands(self):
        commands = ["discovery", "Start quick discovery", "What do you already know?", "What's missing?", "Generate snapshot", "Pause discovery", "Stop discovery", "Stop", "Generate final report", "Generate discovery report", "Resume discovery", "Deepen discovery", "Show full questionnaire"]
        active = ("discovery", "start_quick_discovery", "resume", "deepen")
        for c in commands:
            a = fresh(); a["session"].update(command="  " + c.upper().replace(" ", "  ") + "  ", status="active", exported=True)
            n = vc.normalize_command(c)
            if n == "deepen":
                a["session"].update(**{"pass": 2, "deepen_authorized": True, "substantive_answers": 6})
            if n in active:
                a["session"].update(emitted_questions=["What markets are served?"], emitted_question_ids=["Q01.01"])
            self.check(a, True)
            if n == "deepen":
                a["session"]["deepen_authorized"] = False; self.check(a, False)
                a["session"]["deepen_authorized"] = True; a["session"]["pass2_declined"] = True; self.check(a, False)
            if n not in active:
                a["session"].update(emitted_questions=["One question?"], emitted_question_ids=["Q01.01"]); self.check(a, False)
        a = fresh(); a["session"].update(command="Start quick discovery", status="active", substantive_answers=6, emitted_questions=["One more?"], emitted_question_ids=["Q01.01"]); self.check(a, False)

    def test_malformed_arrays(self):
        muts = [lambda a: a.__setitem__("evidence", {}), lambda a: a.__setitem__("assessments", {}),
                lambda a: a["assessments"][0].__setitem__("facet_results", {}),
                lambda a: a["assessments"][0]["facet_results"][0].__setitem__("qualifier_results", {}),
                lambda a: a["assessments"][0]["facet_results"][0].__setitem__("missing", {}),
                lambda a: a["assessments"][0]["facet_results"][0].__setitem__("qualifier_results", [None]),
                lambda a: a["session"].__setitem__("emitted_questions", {}),
                lambda a: a["assessments"][0]["independent_state"].__setitem__("conflicts", {})]
        for m in muts:
            a = fresh(); m(a); self.check(a, False)


# ---------------------------------------------------------------- review-reproductions-corrected.mjs (25)
def ev1(a, text, **extra):
    e = {"evidence_id": "E1", "locator": "review#1", "exact_excerpt": text, "scope": "general", "temporal": "current", "status": "factual", "actor": "team", "population": "current team buyer operations", "period": "assessment date"}
    e.update(extra); a["evidence"].append(e); return ["E1"]


def credit1(a, qid, i=0, extent="complete"):
    f = facet(a, qid, i)
    f.update(extent=extent, evidence_refs=["E1"], bounds_result="matched", bounds_explanation="Explicitly scoped requested event and actor.", explanation="Review scenario supplies requested answer.")
    for z in f["qualifier_results"]:
        z.update(result="supported", evidence_refs=["E1"], basis="explicit_first" if z["qualifier_id"].endswith(".first") else "Requested predicate explicitly addressed, including supported negative where applicable.")
    f["missing"] = EM(f)
    return f


def active(a, **extra):
    a["session"].update(status="active", command="discovery", emitted_questions=["What is the current service area?"], emitted_question_ids=["Q01.01"], exported=False)
    a["session"].update(extra)


class SuiteReproductions(unittest.TestCase):
    def run_case(self, mutate, expected, binding=None):
        a = fresh(); mutate(a); r = validate(a, binding)
        self.assertEqual("VALID" if r["valid"] else "INVALID", expected, r["errors"][:5]); return r

    def test_all(self):
        P = "pass"
        self.run_case(lambda a: active(a, substantive_answers=6), "INVALID")
        self.run_case(lambda a: a["session"].update(substantive_answers=6), "VALID")
        self.run_case(lambda a: active(a, **{P: 2, "substantive_answers": 6, "deepen_authorized": True}), "VALID")
        self.run_case(lambda a: active(a, **{P: 2, "substantive_answers": 6}), "INVALID")
        self.run_case(lambda a: active(a, **{P: 2, "deepen_authorized": True, "pass2_declined": True}), "INVALID")
        self.run_case(lambda a: active(a, **{P: 2, "deepen_authorized": True, "command": "Deepen discovery"}), "VALID")
        self.run_case(lambda a: active(a, **{P: 2, "deepen_authorized": True, "command": "Generate snapshot"}), "INVALID")
        self.run_case(lambda a: (ev1(a, "We do not hand buyers between agents."), credit1(a, "Q11.13", 0), credit1(a, "Q11.13", 1)), "VALID")

        def na(a):
            ev1(a, "Our process does not have a second appointment.")
            row(a, "Q09.03")["independent_state"]["applicability"] = {"status": "not_applicable", "evidence_refs": ["E1"], "reason": "No second appointment, so no inter-appointment owner interval.", "scope": "Current team process"}
        r = self.run_case(na, "VALID")
        self.assertEqual(next(x for x in r["rows"] if x["question_id"] == "Q09.03")["label"], "unresolved")

        def unknown_not_negative(a):
            f = facet(a, "Q11.13", 1); f["extent"] = "complete"; f["missing"] = EM(f)
        self.run_case(unknown_not_negative, "INVALID")
        self.run_case(lambda a: (ev1(a, "This buyer entered through our active paid Meta campaign today.", scope="case"), credit1(a, "Q02.01", 0, "some")), "VALID")
        self.run_case(lambda a: a.__setitem__("bank_sha256", "wrong"), "INVALID")
        self.run_case(lambda a: a["assessments"][0]["facet_results"][0].__setitem__("extent", "half"), "INVALID")

        def q01(attr, val):
            def m(a):
                ev1(a, "Our service area is A."); f = credit1(a, "Q01.01")
                if attr == "qualifier":
                    f["qualifier_results"][0]["result"] = "unknown"
                else:
                    f[attr] = val
                f["missing"] = EM(f)
            return m
        self.run_case(q01("qualifier", None), "INVALID")
        self.run_case(q01("bounds_result", "mismatch"), "INVALID")
        self.run_case(q01("conflict", "unresolved"), "INVALID")
        self.run_case(lambda a: (ev1(a, "Probably the tour agent.", status="analytic"), credit1(a, "Q11.08")), "INVALID")
        self.run_case(lambda a: a["assessments"][0]["facet_results"].append(dict(a["assessments"][0]["facet_results"][0], facet_id="invented")), "INVALID")
        self.run_case(lambda a: a["assessments"][0].__setitem__("missing_summary", []), "INVALID")
        self.run_case(lambda a: a["assessments"][0]["facet_results"][0].__setitem__("missing", []), "INVALID")
        self.run_case(lambda a: a.__setitem__("evidence", {}), "INVALID")
        self.run_case(lambda a: (active(a), a["assessments"][0]["independent_state"].update(deferred=True, defer_reason="Deferred by owner")), "INVALID")
        self.run_case(lambda a: (active(a), a["assessments"][0]["independent_state"].update(not_tracked=True, not_tracked_reason="Unavailable")), "INVALID")
        m = {"schema_version": "1.0.0", "units": [{"locator": "review#1", "text": "The coordinator conducts the tour."}]}
        b = {"map": m, "sha256": vc.sha256(vc.stringify(m))}
        self.run_case(lambda a: (ev1(a, m["units"][0]["text"]), credit1(a, "Q11.08"), a.__setitem__("source_map_sha256", b["sha256"])), "VALID", b)
        self.run_case(lambda a: (ev1(a, "Invented quote"), credit1(a, "Q11.08"), a.__setitem__("source_map_sha256", b["sha256"])), "INVALID", b)

    def test_blank_template_valid(self):
        r = validate(fresh())
        self.assertTrue(r["valid"])
        self.assertEqual(r["counts"], {"fully_answered": 0, "partially_answered": 0, "unresolved": 332})


if __name__ == "__main__":
    unittest.main()
