"""
VerifAI Candidate Scrutiny & Document Verification Engine
Inspired by production admissions evaluation at institutions like Goa Institute of Management (GIM)
and national-scale scrutiny portals.

Matches OCR-extracted document records against candidate application inputs,
validating academic cutoffs, identity/age constraints, and certificate authenticity.
"""

from datetime import date, datetime, timezone
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class DocumentType(str, Enum):
    DEGREE_CERTIFICATE = "DEGREE_CERTIFICATE"
    MARKSHEET_10TH = "MARKSHEET_10TH"
    MARKSHEET_12TH = "MARKSHEET_12TH"
    EXPERIENCE_CERTIFICATE = "EXPERIENCE_CERTIFICATE"
    GOVERNMENT_ID = "GOVERNMENT_ID"


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    DISCREPANCY_FLAGGED = "DISCREPANCY_FLAGGED"
    REJECTED = "REJECTED"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"


class DiscrepancySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    CRITICAL = "CRITICAL"


class VerificationFlag(BaseModel):
    field: str
    severity: DiscrepancySeverity
    claimed_value: Any
    extracted_value: Any
    reason: str


class ExtractedDocumentData(BaseModel):
    document_type: DocumentType
    document_id: Optional[str] = None
    candidate_name: str
    institution_or_issuer: str
    issue_date: Optional[date] = None
    date_of_birth: Optional[date] = None
    percentage_or_cgpa: Optional[float] = None
    cgpa_scale: Optional[float] = 10.0
    tenure_months: Optional[int] = None
    confidence_score: float = Field(ge=0.0, le=1.0)


class CandidateApplicationProfile(BaseModel):
    application_id: str
    full_name: str
    date_of_birth: date
    qualifying_degree: str
    claimed_cgpa: float
    claimed_work_ex_months: int = 0
    program_applied: str = "PGDM / MBA"


class ScrutinyReport(BaseModel):
    application_id: str
    candidate_name: str
    overall_status: VerificationStatus
    eligibility_cutoff_met: bool
    audit_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    flags: List[VerificationFlag] = []
    confidence_aggregate: float
    playbook_action: str


class VerifAIScrutinyEngine:
    """
    Core verification pipeline used by Forward Deployed Engineers to configure
    and execute deterministic scrutiny rules for enterprise admissions and HR clients.
    """

    def __init__(self, min_cgpa_cutoff: float = 6.0, min_age: int = 20, max_age: int = 35):
        self.min_cgpa_cutoff = min_cgpa_cutoff
        self.min_age = min_age
        self.max_age = max_age

    def _normalize_name(self, name: str) -> str:
        return "".join(name.lower().split())

    def _calculate_age(self, dob: date, reference_date: date) -> int:
        return reference_date.year - dob.year - (
            (reference_date.month, reference_date.day) < (dob.month, dob.day)
        )

    def evaluate_candidate(
        self,
        application: CandidateApplicationProfile,
        extracted_docs: List[ExtractedDocumentData],
        reference_deadline: Optional[date] = None
    ) -> ScrutinyReport:
        if reference_deadline is None:
            reference_deadline = date.today()

        flags: List[VerificationFlag] = []
        confidences: List[float] = [doc.confidence_score for doc in extracted_docs] or [0.0]
        avg_confidence = sum(confidences) / len(confidences)

        # 1. Validate Candidate Age against Cutoff
        candidate_age = self._calculate_age(application.date_of_birth, reference_deadline)
        if candidate_age < self.min_age or candidate_age > self.max_age:
            flags.append(
                VerificationFlag(
                    field="date_of_birth",
                    severity=DiscrepancySeverity.CRITICAL,
                    claimed_value=application.date_of_birth.isoformat(),
                    extracted_value=f"Age: {candidate_age}",
                    reason=f"Candidate age {candidate_age} outside allowable bracket [{self.min_age}, {self.max_age}]"
                )
            )

        # 2. Check Name Consistency Across Extracted Documents
        norm_app_name = self._normalize_name(application.full_name)
        for doc in extracted_docs:
            norm_doc_name = self._normalize_name(doc.candidate_name)
            if norm_app_name not in norm_doc_name and norm_doc_name not in norm_app_name:
                flags.append(
                    VerificationFlag(
                        field="candidate_name",
                        severity=DiscrepancySeverity.CRITICAL,
                        claimed_value=application.full_name,
                        extracted_value=doc.candidate_name,
                        reason=f"Name mismatch detected in {doc.document_type.value}"
                    )
                )

        # 3. Check Academic Cutoff & Claimed vs Extracted Marks
        degree_docs = [
            d for d in extracted_docs
            if d.document_type in (DocumentType.DEGREE_CERTIFICATE, DocumentType.MARKSHEET_12TH)
            and d.percentage_or_cgpa is not None
        ]

        cutoff_met = True
        if degree_docs:
            primary_deg = degree_docs[0]
            # Normalize to 10-point scale if in percentage (> 10)
            extracted_cgpa = primary_deg.percentage_or_cgpa
            if extracted_cgpa > 10.0:
                extracted_cgpa = extracted_cgpa / 10.0

            if extracted_cgpa < self.min_cgpa_cutoff:
                cutoff_met = False
                flags.append(
                    VerificationFlag(
                        field="academic_cutoff",
                        severity=DiscrepancySeverity.CRITICAL,
                        claimed_value=application.claimed_cgpa,
                        extracted_value=extracted_cgpa,
                        reason=f"Academic score {extracted_cgpa:.2f} falls below institutional cutoff {self.min_cgpa_cutoff}"
                    )
                )

            # Check if claimed CGPA is inflated compared to verified OCR
            if application.claimed_cgpa > (extracted_cgpa + 0.3):
                flags.append(
                    VerificationFlag(
                        field="cgpa_inflation",
                        severity=DiscrepancySeverity.MEDIUM,
                        claimed_value=application.claimed_cgpa,
                        extracted_value=extracted_cgpa,
                        reason=f"Claimed score {application.claimed_cgpa} exceeds verified certificate score {extracted_cgpa:.2f}"
                    )
                )

        # 4. Check Work Experience Verification
        exp_docs = [
            d for d in extracted_docs
            if d.document_type == DocumentType.EXPERIENCE_CERTIFICATE
            and d.tenure_months is not None
        ]
        total_extracted_exp = sum(d.tenure_months or 0 for d in exp_docs)
        if application.claimed_work_ex_months > 0 and (total_extracted_exp < application.claimed_work_ex_months - 2):
            flags.append(
                VerificationFlag(
                    field="work_experience",
                    severity=DiscrepancySeverity.MEDIUM,
                    claimed_value=application.claimed_work_ex_months,
                    extracted_value=total_extracted_exp,
                    reason=f"Verified work tenure ({total_extracted_exp} mo) does not substantiate claimed ({application.claimed_work_ex_months} mo)"
                )
            )

        # 5. Determine Overall Verdict
        has_critical = any(f.severity == DiscrepancySeverity.CRITICAL for f in flags)
        has_medium = any(f.severity == DiscrepancySeverity.MEDIUM for f in flags)

        if has_critical:
            overall_status = VerificationStatus.REJECTED
            action = "Escalate to Admissions Committee: candidate fails mandatory institutional criteria."
        elif has_medium or avg_confidence < 0.75:
            overall_status = VerificationStatus.MANUAL_REVIEW_REQUIRED
            action = "Queue for Secondary Officer Review in Interactive Verification Workbench."
        else:
            overall_status = VerificationStatus.VERIFIED
            action = "Direct Pass: Auto-approve candidate for stage-2 interview/offer generation."

        return ScrutinyReport(
            application_id=application.application_id,
            candidate_name=application.full_name,
            overall_status=overall_status,
            eligibility_cutoff_met=cutoff_met,
            flags=flags,
            confidence_aggregate=round(avg_confidence, 3),
            playbook_action=action
        )
