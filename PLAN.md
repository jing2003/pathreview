## Solution plan

**Issue:** [Add a safety event count to the health check endpoint](https://github.com/ascherj/pathreview/issues/68)

### Understand

The `/health` endpoint currently includes a `safety_events_last_hour` field, but the value is hard-coded to `0`. Because the route never reads from `SafetyMonitor`, it reports zero even after safety events have been recorded in Redis.

`SafetyMonitor` already records counters for valid event types such as `pii_detected`, `injection_attempt`, `content_filtered`, `bias_detected`, and `rate_limited`. However, `get_event_count()` only retrieves one event type at a time, and its `window_hours` argument is not currently enforced. The expected result is for the health response to report a real safety-event count instead of the placeholder value while keeping the endpoint's existing dependency checks and error handling.

### Map

Files and code areas involved:

- `api/routes/health.py`
  - `health_check()`
  - Currently initializes and later reassigns `safety_events_last_hour` to `0`
  - Will need to read the safety-event count from the monitoring layer

- `safety/monitoring.py`
  - `SafetyMonitor.VALID_EVENT_TYPES`
  - `SafetyMonitor.log_event()`
  - `SafetyMonitor.get_event_count()`
  - May need a helper that totals counts across all valid event types

- `tests/unit/test_health.py` — expected new or existing test file
  - Add tests for the health endpoint's safety-event field

- `tests/unit/test_safety_monitoring.py` — only if monitoring behavior changes
  - Add tests for any new aggregation helper or time-window behavior

### Plan

1. Confirm the current behavior by recording a valid safety event through `SafetyMonitor`, verifying that its Redis counter increases, and confirming that `/health` still returns `safety_events_last_hour: 0`.

2. Add a monitoring-layer method that calculates the total safety-event count across all values in `SafetyMonitor.VALID_EVENT_TYPES`. Keep the aggregation logic inside `safety/monitoring.py` so the health route does not duplicate monitoring details.

3. Update `health_check()` in `api/routes/health.py` to create or reuse a Redis client, initialize `SafetyMonitor`, and replace the hard-coded value with the count returned by the monitoring layer.

4. Preserve graceful failure behavior. If Redis or the monitoring lookup fails, log the error and leave `safety_events_last_hour` as `0` instead of causing an unhandled exception.

5. Add focused tests for no events, one event type, multiple event types, and monitoring failures. Run the repository's relevant unit tests and code-quality checks before committing the implementation.

### Inputs & outputs

#### Inputs

- The Redis client used by the application
- Redis counters stored under keys in the format `safety:events:<event_type>`
- The valid event types defined by `SafetyMonitor.VALID_EVENT_TYPES`

#### Outputs

The `/health` endpoint should continue returning its existing health information. The value should be a nonnegative integer:

- `0` when no safety events are available
- A positive total when safety counters exist
- `0` when the monitoring lookup fails and the error is handled gracefully

### Risks & unknowns

- The current Redis counters expire after 24 hours, not one hour.
- The `window_hours` parameter in `get_event_count()` is documented but not enforced.
- Summing the current counters would provide a real safety-event total, but it might include events older than one hour.
- Implementing a true rolling one-hour window may require changing how events are stored, which could expand the scope beyond a small Tier 1 issue.
- The intended behavior should be confirmed through the issue discussion, existing tests, or maintainer/instructor guidance before changing the Redis storage design.
- Redis failures should not remove the existing dependency status information or crash the endpoint.

### Edge cases

- No safety-event keys exist in Redis.
- Only one valid event type has a stored count.
- Several valid event types have stored counts that must be combined.
- A Redis key expires while the health request is being processed.
- Redis returns no value for a valid event type.
- Redis raises an exception during the count lookup.
- An unknown event type exists in Redis and should not be counted.
- Another dependency is unhealthy and the endpoint returns `503`.
- A monitoring failure occurs while PostgreSQL, Redis ping, and vector-database checks are otherwise healthy.
