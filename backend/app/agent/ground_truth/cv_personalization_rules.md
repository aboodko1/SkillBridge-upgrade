# CV personalization rules for the roadmap validator

The validator must distinguish, per role competency, whether the student's CV
DEMONSTRATES it, merely LISTS it, or says nothing (UNKNOWN). The roadmap is
personalized when it treats each status correctly:

| Status      | Meaning                                                      | Roadmap treatment                    |
|-------------|--------------------------------------------------------------|--------------------------------------|
| DEMONSTRATED | The CV shows concrete project/artifact evidence of the skill | Assessment-first or advanced module; **never a beginner module** |
| LISTED      | The CV names the skill but with no artifact evidence         | Assessment-first module              |
| UNKNOWN     | The CV says nothing about the skill                          | Full teaching module                  |

A roadmap is penalised (lower `personalization_score`) when it frames a
DEMONSTRATED or LISTED skill at beginner level, and flagged `CV_REDUNDANCY`
when it teaches a DEMONSTRATED skill from scratch.

## Hard requirements for the reference CV ("Khaled")

1. Do NOT recommend beginner **Python**. The CV demonstrates a Python SQL
   Injection Detector tool.
2. Do NOT recommend beginner **Java**. The CV shows three Java projects.
3. Do NOT recommend beginner **communication/teaching**. The CV shows peer
   teaching and presentation experience.
4. KEEP **SIEM querying** as an assessment-first module. The CV shows log
   *generation* (ELK/Splunk event-log simulator), not *querying* — do not
   conflate the two.
5. KEEP **triage**, **escalation**, **MITRE ATT&CK**, **incident response**,
   **ticketing**, and **threat intelligence** as full modules — all are
   UNKNOWN from the CV.
6. The `personalization_score` for this CV must land between **0.40 and 0.55**.
   Above 0.7 is too generous; below 0.2 ignores the CV evidence.

## Deterministic classification

The no-LLM fallback (`_deterministic_violations`) classifies skills by keyword
evidence:

- **DEMONSTRATED** — the CV contains both the skill term and an artifact
  evidence token (e.g. "sql", "scapy", "project", "teaching", "presentation").
- **LISTED** — the CV contains the skill term but no artifact evidence token
  (e.g. "networking basics", "penetration testing", "SIEM" mentioned as a
  tool without a querying artifact).
- **UNKNOWN** — the skill term is absent from the CV.

`personalization_score` = `handled / known`, where `known` is the number of
DEMONSTRATED + LISTED skills found in the CV and `handled` is the number of
those the roadmap does not frame at beginner level. When the CV yields no known
skills, personalization defaults to 1.0 (nothing to personalize against).