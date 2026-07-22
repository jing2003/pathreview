# PathReview Contribution Journal

## Week 7 — Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/68

**Issue title:** Add a safety event count to the health check endpoint

**Tier:** [x] Tier 1 [ ] Tier 2 [ ] Tier 3

**Problem summary:**

The `/health` API endpoint checks the status of the application's dependencies, but its safety event metric currently uses a placeholder value of zero. This means operators cannot use the health endpoint to determine whether safety-related events have recently occurred. The relevant code is primarily located in `api/routes/health.py` and `safety/monitoring.py`, where safety events are recorded using Redis counters. A successful fix will return a meaningful `safety_events_last_hour` count while preserving the endpoint's existing dependency health checks and error handling.

**Branch name:** `fix/68-safety-event-count-health-check`

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger

### "Is this issue right for me?" checklist reasoning

- The issue has a clearly defined expected result: the health endpoint should report recent safety event activity.
- The issue identifies the two main files involved, which keeps the initial investigation focused.
- It is labeled Tier 1 and has an estimated effort of two to four hours, making the scope appropriate for a first contribution to this codebase.
- The change appears limited to the API and safety monitoring components and should not require frontend work or a database migration.
- The existing health endpoint already contains a placeholder `safety_events_last_hour` field, so the primary task is connecting it to actual monitoring data and adding relevant tests.
- One scope detail that requires investigation is that the current safety monitoring counters expire after 24 hours and the `window_hours` parameter is not currently enforced. I will examine the existing tests and usage patterns before deciding how the one-hour count should be calculated.

## Week 8 — Reproduction & solution planning

**Reproduction commit link:**

**Reproduction summary:**

I reproduced the issue by logging a safety event through `SafetyMonitor` and confirming that the corresponding Redis counter increased. However, the `/health` endpoint still returned `safety_events_last_hour: 0` because the value is currently hard-coded instead of being read from the safety monitoring counters.

**PLAN.md link:**

**Walkthrough video:** [issue reproduction walkthrough](https://drive.google.com/file/d/1O_rCACSvW8Om-m6tdWctpGYgcKOivh-g/view?usp=sharing)

**Blockers or open questions:**
