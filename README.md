# AltUni AI Forward Deployed Engineer (FDE) Deployment Playbook & Evaluation Suite

**Author:** Vinay Kondabathula  
**Ecosystem:** [AltUni AI Labs by InsideIIM](https://altunilabs.ai)  
**Products Covered:** KonverseAI (Voice-first AI Interviewing) & VerifAI / PotentialAI (Candidate Scrutiny & Document Verification)

---

## Overview

This repository demonstrates the practical engineering, prompt configuration, and deployment playbooks required of an **AI Forward Deployed Engineer (FDE)** at AltUni AI Labs. 

As an FDE, technical capability must extend beyond theoretical machine learning into real-world client implementations:
1. Translating customer requirements (universities and Fortune 500 employers) into reliable AI pipelines.
2. Building deterministic evaluation harnesses, Pydantic schemas, and fallback guardrails.
3. Conducting stakeholder enablement, live demos, and converting each implementation into reusable playbooks.

---

## Repository Structure

```
altuni-fde-playbook/
├── README.md                                 # Architecture overview & executive summary
├── playbooks/
│   ├── admissions_verifai_playbook.md        # SOP: Deploying VerifAI for Admissions (GIM case study)
│   └── campus_konverse_playbook.md           # SOP: Deploying KonverseAI for Campus Hiring (HUL/Axis case study)
├── src/
│   ├── __init__.py                           # Exported modules
│   ├── verifai_scrutiny.py                   # Pydantic document verification & scrutiny engine
│   └── konverse_evaluator.py                 # Deterministic rubric scoring & evasion detection engine
└── tests/
    └── test_playbook.py                      # Deterministic unit test suite
```

---

## Key Modules

### 1. `verifai_scrutiny.py` (Admissions & Candidate Verification)
- **Problem Solved:** Educational institutions (like Goa Institute of Management evaluating 8,000+ applicants) and campus recruiters face massive backlogs verifying candidate documents against application claims.
- **Implementation:**
  - Ingests OCR/CV extracted document data into strictly typed `Pydantic` schemas.
  - Automatically checks institutional eligibility rules: statutory age limits, degree cutoffs, and work tenure validation.
  - Detects CGPA inflation, university accreditation discrepancies, and name mismatches.
  - Outputs an explainable `ScrutinyReport` with an actionable verdict: `VERIFIED`, `MANUAL_REVIEW_REQUIRED`, or `REJECTED`.

### 2. `konverse_evaluator.py` (Voice/Text AI Interview Rubrics)
- **Problem Solved:** Enterprise recruiters (HUL, Axis Bank, TCPL) need standardized, unbiased interview evaluations across tens of thousands of applicants.
- **Implementation:**
  - Evaluates candidate interview answers across customizable weighted competency dimensions.
  - Detects evasion, generic canned responses, or prompt injections.
  - Aggregates dimension scores into hiring recommendations (`STRONG_HIRE`, `HIRE`, `BORDERLINE`, `NO_HIRE`) and generates individualized candidate development feedback.

---

## Running the Evaluation Suite

The test suite runs with zero third-party dependencies beyond standard Python 3.10+ and Pydantic:

```bash
# Run unit tests
python -m unittest tests/test_playbook.py
```

Expected output:
```
...
----------------------------------------------------------------------
Ran 3 tests in 0.002s

OK
```

---

## Alignment with Real Enterprise Deployments

This suite directly builds upon my operational experience at **BISAG-N (Ministry of Electronics and IT)**, where I engineered the end-to-end AI document scrutiny and OCR extraction engine for national candidate verification portals, and conducted client stakeholder meetings with senior officials to turn manual verification guidelines into deterministic software pipelines.
