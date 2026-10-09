# FDE Playbook: Deploying VerifAI & PotentialAI Admit for Higher Education Admissions

**Author:** Vinay Kondabathula (AI Forward Deployed Engineer)  
**Target Clients:** Higher Education Institutions (e.g., Goa Institute of Management, Top B-Schools)  
**Objective:** Automate application document scrutiny, eligibility verification, and candidate profile audit to compress application-to-offer timelines by >60% while eliminating manual verification errors.

---

## 1. Discovery & Requirement Scoping (Days 1–3)

### 1.1 Institutional Stakeholder Alignment
* **Primary Stakeholders:** Admissions Director, Dean of Academics, Verification Officers, Admissions Operations Team.
* **Intake Discovery Checklist:**
  1. *Program Eligibility Rules:* What are the hard cutoffs? (e.g., minimum 50% / 6.0 CGPA in undergraduate degree, approved universities, entrance exam thresholds like CAT/XAT/GMAT).
  2. *Document Matrix:* What documents must be submitted and verified? (10th marksheet, 12th marksheet, Graduation degree & consolidated marksheets, Work Experience certificates, Category certificates).
  3. *Tolerances & Discrepancies:* What constitutes a hard reject vs. manual officer review? (e.g., name spelling variations vs. fabricated CGPA).

---

## 2. Pipeline Configuration & Schema Enforcement (Days 4–7)

### 2.1 Optical & Computer Vision Layer
* **Document Deskewing & Orientation:** Configure automated image deskewing (via MobileNetV3 orientation classifiers) to catch inverted smartphone scans submitted by candidates.
* **Extraction Quality Filter:** Reject and prompt candidates for immediate re-upload if raw document resolution or OCR confidence drops below 0.70.

### 2.2 Pydantic Schema Mapping
Deploy structured JSON extraction schemas (`src/verifai_scrutiny.py`) ensuring zero schema hallucinations:
```json
{
  "application_id": "APP-2026-XXXX",
  "extracted_data": {
    "candidate_name": "Full Name from Certificate",
    "institution": "University / College Name",
    "cgpa_or_percentage": 8.42,
    "issue_date": "2024-06-30",
    "tenure_months": 24
  },
  "confidence_score": 0.94
}
```

---

## 3. Scrutiny Rules & Deterministic Guardrails (Days 8–10)

```
[Candidate Application Submission]
              │
              ▼
    [OCR & CV Deskewing]
              │
              ▼
[Pydantic Structured Extraction]
              │
              ▼
  [Deterministic Scrutiny Engine]
   ├── Age Bracket Check (e.g. 20-30 yrs)
   ├── Academic Cutoff Verification (e.g. CGPA >= 6.0)
   ├── Name Matching (Levenshtein / Token Match)
   └── Work Experience Tenure Check
              │
      ┌───────┴────────────────────────┐
      ▼                                ▼
[Direct Auto-Verified]      [Discrepancy Flagged]
(Top 70% clean apps)                   │
                                       ▼
                       [Interactive Officer Workbench]
                       (Split-pane PDF canvas + OCR overlay)
```

### 3.1 Hard Reject vs. Manual Review Thresholds
* **Direct Rejection:** Candidate age outside statutory limits, unaccredited fake university detected, or actual degree percentage strictly below institutional cutoff.
* **Flagged for Manual Review:**
  * Slight name discrepancy (e.g., surname initials reversed).
  * Missing final semester transcript with provisional certificate provided.
  * Extracted work tenure within 1–2 months of claimed tenure.

---

## 4. User Enablement & Interactive Workbench Onboarding (Days 11–13)

### 4.1 Officer Enablement Sessions
* Run 2 interactive training webinars with admissions scrutiny officers.
* Train officers on the **Interactive Verification Workbench**:
  * Dual-pane synchronized viewing: PDF canvas on the left, extracted Pydantic fields on the right.
  * Clicking an extracted data field instantly pans and highlights the corresponding bounding box on the original PDF.
  * Single-click discrepancy approval or rejection override with audit remarks.

---

## 5. Live Production Monitoring & SLA Escalation (Post-Launch)

* **Daily Throughput Target:** Process 1,500+ applications/day during peak admission cycles.
* **Audit Trail Log:** Every algorithmic verification verdict logs timestamp, confidence score, raw extracted fields, and applied rules into an immutable audit table.
* **Weekly Calibration Review:** FDE meets weekly with Admissions Operations to review flagged false positives and tune extraction prompt templates.
