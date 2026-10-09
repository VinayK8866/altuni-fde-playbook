# FDE Playbook: Deploying KonverseAI for High-Volume Enterprise Campus Hiring

**Author:** Vinay Kondabathula (AI Forward Deployed Engineer)  
**Target Clients:** Enterprise Corporate Talent Teams (e.g., Hindustan Unilever, Axis Bank, Tata Consumer Products)  
**Objective:** Scale voice-first AI interviewing across 10,000+ campus applicants in 48–72 hours with standardized, unbiased candidate scoring and actionable feedback.

---

## 1. Enterprise Client Alignment & Competency Modeling (Week 1)

### 1.1 Discovery with Talent Acquisition (TA) Leadership
* **Key Stakeholders:** Head of Campus Recruitment, Lead Technical Interviewers, Employer Branding Lead.
* **Competency Framework Mapping:**
  Translate client hiring criteria into weighted dimensions:
  1. *Functional Problem Solving (Weight: 40%):* Ability to structure ambiguous business problems, apply domain logic, and propose testable solutions.
  2. *Communication & Executive Presence (Weight: 30%):* Concise articulation, active listening, structured speaking (e.g. STAR method).
  3. *Domain/Technical Aptitude (Weight: 20%):* Role-specific fundamentals (e.g., supply chain metrics, financial ratios, or coding constructs).
  4. *Behavioral & Culture Fit (Weight: 10%):* Adaptability, collaboration, and learning mindset.

---

## 2. Conversational Prompt Engineering & Dynamic Flow Design (Week 2)

### 2.1 KonverseAI Conversational Flow Structure
```
[Introduction & Candidate Verification]
                 │
                 ▼
     [Question 1: Foundational Case]
                 │
                 ▼
[Candidate Voice Response Stream] ──► [Real-Time Transcription]
                 │
                 ▼
       [Dynamic Follow-up Probing]
       (If answer is shallow, probe deeper:
        "Can you elaborate on how you handled the latency constraint?")
                 │
                 ▼
     [Question 2: Behavioral / Culture Scenario]
                 │
                 ▼
     [Question 3: Live Analytical Estimation]
                 │
                 ▼
   [Instant Closing & Next Steps]
```

### 2.2 Anti-Evasion & Anti-Cheating Guardrails
Configure runtime guardrail prompts to flag:
* **Canned / Generic Memorized Scripts:** Candidate recites generic internet answers without answering specific situational constraints.
* **Whisper / Third-Party Assistance Detection:** Detect multiple speakers, unnatural long pauses before complex technical answers, or repetitive verbatim LLM outputs.
* **Evasion Index:** Trigger conversational intervention if candidate avoids answering direct numerical or technical questions.

---

## 3. Rubric Calibration & Pilot Batch Testing (Week 3)

### 3.1 Pilot Calibration Run (100–200 Sample Candidates)
1. Run a closed pilot with past intern profiles or internal interviewers.
2. Generate automated rubric scores using `src/konverse_evaluator.py`.
3. Compare KonverseAI scores against senior human interviewers to calculate **Inter-Rater Agreement (Cohen's Kappa $\ge$ 0.82)**.
4. Tune score thresholds (`hire_threshold=7.5`, `strong_hire_threshold=8.8`) to match client funnel targets.

---

## 4. Live Campus Drive Execution & Infrastructure Readiness (Week 4)

### 4.1 Scalability & Concurrency Readiness
* Provision voice streaming & inference capacity for peak loads (e.g. 5,000 concurrent interviews during nationwide campus slotting).
* Implement graceful degrading: fallback from low-latency voice WebSocket to asynchronous audio chunk evaluation if network packet loss > 15%.

### 4.2 Candidate Experience & Tech Support
* Pre-interview system check (mic, audio, webcam, network speed).
* Real-time automated troubleshooting bot for candidates experiencing audio drops.

---

## 5. Post-Interview Reporting & Candidate Feedback Delivery

* **Executive Dashboard for HR:** Instant candidate rankings, competency score breakdowns, flagged anomalies, and interview audio recordings.
* **Candidate Value-Add Feedback:** Provide every candidate with an instant constructive report (Top Strengths & Growth Areas) reinforcing positive employer brand perception.
* **Playbook Post-Mortem:** Document client-specific nuances, updated question banks, and failure mode calibrations to feed back into core engineering.
