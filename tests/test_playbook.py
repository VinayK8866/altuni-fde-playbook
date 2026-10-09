"""
Unit tests for AltUni FDE VerifAI & KonverseAI engines using standard unittest.
Validates candidate document scrutiny, cutoff evaluations, rubric aggregations,
and anomaly flagging.
"""

from datetime import date
import unittest
import sys
import os

# Add parent directory to sys.path so src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.verifai_scrutiny import (
    VerifAIScrutinyEngine,
    CandidateApplicationProfile,
    ExtractedDocumentData,
    DocumentType,
    VerificationStatus,
    DiscrepancySeverity
)
from src.konverse_evaluator import (
    KonverseRubricEvaluator,
    InterviewQuestionEvaluation,
    CompetencyDimension,
    EvasionOrCheatingRisk
)


class TestAltUniFDEPlaybook(unittest.TestCase):

    def test_verifai_clean_candidate(self):
        engine = VerifAIScrutinyEngine(min_cgpa_cutoff=6.0, min_age=20, max_age=30)
        profile = CandidateApplicationProfile(
            application_id="APP-2026-001",
            full_name="Aarav Sharma",
            date_of_birth=date(2001, 5, 14),
            qualifying_degree="B.Tech Computer Science",
            claimed_cgpa=8.45,
            claimed_work_ex_months=12,
            program_applied="PGDM Tech"
        )

        docs = [
            ExtractedDocumentData(
                document_type=DocumentType.DEGREE_CERTIFICATE,
                document_id="DEG-77192",
                candidate_name="Aarav Sharma",
                institution_or_issuer="National Institute of Technology",
                percentage_or_cgpa=8.45,
                confidence_score=0.96
            ),
            ExtractedDocumentData(
                document_type=DocumentType.EXPERIENCE_CERTIFICATE,
                document_id="EXP-110",
                candidate_name="Aarav Sharma",
                institution_or_issuer="Tech Corp India",
                tenure_months=12,
                confidence_score=0.92
            )
        ]

        report = engine.evaluate_candidate(profile, docs, reference_deadline=date(2026, 6, 1))
        self.assertEqual(report.overall_status, VerificationStatus.VERIFIED)
        self.assertTrue(report.eligibility_cutoff_met)
        self.assertEqual(len(report.flags), 0)

    def test_verifai_flagged_cgpa_inflation_and_name_mismatch(self):
        engine = VerifAIScrutinyEngine(min_cgpa_cutoff=6.5, min_age=20, max_age=30)
        profile = CandidateApplicationProfile(
            application_id="APP-2026-002",
            full_name="Rohan Verma",
            date_of_birth=date(2002, 1, 10),
            qualifying_degree="B.Com Honors",
            claimed_cgpa=8.9,
            claimed_work_ex_months=0
        )

        docs = [
            ExtractedDocumentData(
                document_type=DocumentType.DEGREE_CERTIFICATE,
                document_id="DEG-9921",
                candidate_name="Rohan Varma",  # slight typo / mismatch
                institution_or_issuer="State University",
                percentage_or_cgpa=6.1,  # Below cutoff & severely inflated
                confidence_score=0.88
            )
        ]

        report = engine.evaluate_candidate(profile, docs, reference_deadline=date(2026, 6, 1))
        self.assertEqual(report.overall_status, VerificationStatus.REJECTED)
        self.assertFalse(report.eligibility_cutoff_met)
        self.assertTrue(any(f.field == "academic_cutoff" for f in report.flags))
        self.assertTrue(any(f.field == "cgpa_inflation" for f in report.flags))

    def test_konverse_rubric_evaluation(self):
        evaluator = KonverseRubricEvaluator(hire_threshold=7.0, strong_hire_threshold=8.5)

        dims_q1 = [
            CompetencyDimension(
                name="Problem Solving",
                weight=0.5,
                score=8.5,
                justification="Clear decomposition of distributed system bottlenecks.",
                key_strengths=["First-principles thinking", "Root cause diagnosis"],
                improvement_areas=["Could elaborate on network edge cases"]
            ),
            CompetencyDimension(
                name="Communication",
                weight=0.5,
                score=9.0,
                justification="Articulate, concise, and structured.",
                key_strengths=["Structured response framework"],
                improvement_areas=[]
            )
        ]

        q1_score = evaluator.calculate_question_score(dims_q1)
        self.assertEqual(q1_score, 8.75)

        eval_q1 = InterviewQuestionEvaluation(
            question_id="Q1",
            question_text="How would you diagnose latency spikes in a high-traffic microservice?",
            candidate_response="I would first inspect p99 latencies, check database connection pool utilization...",
            dimensions=dims_q1,
            weighted_score=q1_score,
            evasion_analysis=EvasionOrCheatingRisk(
                risk_level="LOW",
                flags=[],
                is_canned_or_generic=False
            ),
            actionable_feedback="Strong architectural grasp with immediate tactical triage."
        )

        summary = evaluator.generate_interview_summary(
            candidate_id="CAND-404",
            candidate_name="Priya Nair",
            role_or_program="AI Forward Deployed Engineer",
            evaluations=[eval_q1]
        )

        self.assertEqual(summary.hiring_recommendation, "STRONG_HIRE")
        self.assertEqual(summary.overall_score, 8.75)
        self.assertIn("Problem Solving", summary.dimension_breakdown)
        self.assertGreater(len(summary.strengths), 0)


if __name__ == "__main__":
    unittest.main()
