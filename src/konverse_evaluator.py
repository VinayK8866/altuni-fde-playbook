"""
KonverseAI Interview Evaluation & Rubric Engine
Inspired by AltUni's KonverseAI voice-first interview platform used by enterprise
clients (Hindustan Unilever, Axis Bank campus hiring) and MBA admissions programs.

Enforces deterministic rubric scoring, structured JSON outputs, evasion detection,
and actionable candidate feedback.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class CompetencyDimension(BaseModel):
    name: str
    weight: float = Field(ge=0.0, le=1.0)
    score: float = Field(ge=0.0, le=10.0, description="Score on a 0-10 scale")
    justification: str
    key_strengths: List[str]
    improvement_areas: List[str]


class EvasionOrCheatingRisk(BaseModel):
    risk_level: str = Field(description="LOW, MEDIUM, or HIGH")
    flags: List[str]
    is_canned_or_generic: bool


class InterviewQuestionEvaluation(BaseModel):
    question_id: str
    question_text: str
    candidate_response: str
    dimensions: List[CompetencyDimension]
    weighted_score: float = Field(ge=0.0, le=10.0)
    evasion_analysis: EvasionOrCheatingRisk
    actionable_feedback: str


class CandidateInterviewReport(BaseModel):
    candidate_id: str
    candidate_name: str
    role_or_program: str
    overall_score: float = Field(ge=0.0, le=10.0)
    hiring_recommendation: str = Field(description="STRONG_HIRE, HIRE, BORDERLINE, NO_HIRE")
    dimension_breakdown: Dict[str, float]
    summary_feedback: str
    strengths: List[str]
    areas_for_development: List[str]


class KonverseRubricEvaluator:
    """
    Core rubric engine utilized by Forward Deployed Engineers to calibrate
    client-specific interview prompts, score distributions, and recommendation thresholds.
    """

    def __init__(
        self,
        hire_threshold: float = 7.5,
        strong_hire_threshold: float = 8.8,
        borderline_threshold: float = 6.0
    ):
        self.hire_threshold = hire_threshold
        self.strong_hire_threshold = strong_hire_threshold
        self.borderline_threshold = borderline_threshold

    def calculate_question_score(
        self,
        dimensions: List[CompetencyDimension]
    ) -> float:
        total_weight = sum(d.weight for d in dimensions)
        if total_weight <= 0:
            return 0.0
        weighted_sum = sum(d.score * d.weight for d in dimensions)
        return round(weighted_sum / total_weight, 2)

    def generate_interview_summary(
        self,
        candidate_id: str,
        candidate_name: str,
        role_or_program: str,
        evaluations: List[InterviewQuestionEvaluation]
    ) -> CandidateInterviewReport:
        if not evaluations:
            raise ValueError("Evaluations list cannot be empty.")

        # Aggregate dimension scores across questions
        dim_accum: Dict[str, List[float]] = {}
        all_strengths: List[str] = []
        all_dev_areas: List[str] = []

        total_score_sum = 0.0
        for ev in evaluations:
            total_score_sum += ev.weighted_score
            for dim in ev.dimensions:
                dim_accum.setdefault(dim.name, []).append(dim.score)
                all_strengths.extend(dim.key_strengths)
                all_dev_areas.extend(dim.improvement_areas)

        overall_score = round(total_score_sum / len(evaluations), 2)
        dim_averages = {
            name: round(sum(scores) / len(scores), 2)
            for name, scores in dim_accum.items()
        }

        # Check for any severe evasion across the interview
        high_risk_evasions = [
            ev for ev in evaluations
            if ev.evasion_analysis.risk_level == "HIGH"
        ]

        if high_risk_evasions:
            recommendation = "NO_HIRE"
            summary_feedback = (
                f"Candidate exhibited high evasion / generic script matching across "
                f"{len(high_risk_evasions)} question(s). Did not provide substantiated answers."
            )
        elif overall_score >= self.strong_hire_threshold:
            recommendation = "STRONG_HIRE"
            summary_feedback = (
                "Exceptional depth, structured articulation, and high contextual awareness. "
                "Consistently exceeded role competency bars."
            )
        elif overall_score >= self.hire_threshold:
            recommendation = "HIRE"
            summary_feedback = (
                "Solid competency alignment across technical and behavioral dimensions. "
                "Demonstrated strong problem-solving and communication."
            )
        elif overall_score >= self.borderline_threshold:
            recommendation = "BORDERLINE"
            summary_feedback = (
                "Meets minimum threshold but lacks depth in core areas. "
                "Recommend secondary panel review or targeted technical assessment."
            )
        else:
            recommendation = "NO_HIRE"
            summary_feedback = (
                "Candidate did not meet required competency thresholds for this benchmark."
            )

        # Deduplicate top strengths & areas for development
        top_strengths = list(dict.fromkeys(all_strengths))[:4]
        top_dev_areas = list(dict.fromkeys(all_dev_areas))[:3]

        return CandidateInterviewReport(
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            role_or_program=role_or_program,
            overall_score=overall_score,
            hiring_recommendation=recommendation,
            dimension_breakdown=dim_averages,
            summary_feedback=summary_feedback,
            strengths=top_strengths,
            areas_for_development=top_dev_areas
        )
