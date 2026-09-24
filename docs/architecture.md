# SkillBridge architecture and evidence boundaries

This page is for technical reviewers. The [main README](../README.md) is the
short product story; the code and tests are the implementation authority.

## Request and data flow

```mermaid
sequenceDiagram
    actor Learner as Student
    participant Web as React interface
    participant API as FastAPI
    participant DB as SQLite
    participant Provider as Optional AI or jobs provider

    Learner->>Web: Sign in
    Web->>API: Credentials
    API->>DB: Check password and create expiring session
    API-->>Web: Session token
    Learner->>Web: Choose a target role
    Web->>API: Role, profile, and score requests + session token
    API->>DB: Check ownership and load requirements/evidence
    API-->>Web: Match, gaps, and calculation breakdown
    Learner->>Web: Learn, practise, and assess
    Web->>API: Progress and assessment attempts
    API->>DB: Store results and integrity metadata
    API-->>Web: Self-reported or in-app verified skill state
    Web->>API: Request matching opportunities
    API-->>Provider: Fetch permitted listings when configured/cache requires
    Provider-->>API: External listings or provider error
    API->>DB: Cache/normalize listing data and track saved applications
    API-->>Web: Sourced listings, freshness, or honest fallback state
```

## Three different kinds of evidence

```mermaid
flowchart LR
    CV[CV or student claim] --> SR[Self-reported profile]
    Lesson[Lesson and scenario practice] --> Progress[Learning/practice progress]
    Assessment[Completed in-app assessment] --> Rules[Score and integrity review]
    Rules -->|eligible pass| Verified[Verified within SkillBridge]
    SR --> Match[Role and job-match explanation]
    Progress --> Match
    Verified --> Match
```

These states are deliberately different. A CV or a completed scenario cannot
award a verified skill. “Verified” means only that the app's own assessment
conditions were met; it is not a third-party credential. Browser and camera
integrity signals are fallible heuristics, not biometric identity proof.

## External-provider boundary

| External capability | Local behavior when unavailable | What the UI should say |
|---|---|---|
| AI text provider | Deterministic fallback where supported | Do not label fallback as live AI |
| ElevenLabs speech | Text can remain available; audio may fail | Voice unavailable or quota exhausted |
| Job providers | Other configured providers, cached results, or empty state | Show source, freshness, and provider status |
| SMTP | Local demo verification behavior | Do not claim an email was delivered |

Credentials remain server-side in a local `.env`, never in frontend source or
the public repository. The job feed is a subset of what its providers return;
external listing pages remain authoritative for application details.

## Review map

| Concern | Main code |
|---|---|
| API and authorization | `backend/app/main.py`, `backend/app/auth.py` |
| Database and migrations | `backend/app/database.py`, `backend/app/models.py` |
| Role/job match calculations | `backend/app/matching.py`, `backend/app/match_explain.py` |
| Assessment integrity | `backend/app/integrity.py`, `frontend/src/lib/webcamIntegrity.ts` |
| Jobs providers and caching | `backend/app/jobs.py` |
| AI and speech | `backend/app/genai.py`, `backend/app/tts.py` |
| Student interface | `frontend/src/pages/`, `frontend/src/components/` |

Run the commands in the main README before reviewing. Tests and local smoke
checks are useful evidence, but live provider availability depends on valid
configuration and quota at the time of the demo.
