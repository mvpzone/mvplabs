-- =============================================================================
-- LAB 2 — Query 2: Behavioral Anomaly Detection
-- =============================================================================
-- Find events where behavioral signals indicate anomalous activity.
--
-- WHAT TO LOOK FOR:
--   - Safety flags (is_flagged = TRUE): content safety triggers
--   - High token consumption: potential prompt injection or data exfiltration
--   - Unusual tool patterns: tools not normally called by this agent
--   - Timing anomalies: events outside business hours or rapid-fire sequences
--
-- TABLE: pyagents.session_events_log
-- =============================================================================

-- 2a. Flagged events (safety triggers)
SELECT
  event_id,
  session_id,
  author,
  attestation.agent_name,
  attestation.model_id,
  annotations.flag_types,
  annotations.input_tokens,
  annotations.output_tokens,
  event_ts
FROM `pyagents.session_events_log`
WHERE annotations.is_flagged = TRUE
  AND event_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
ORDER BY event_ts DESC;

-- 2b. High token consumption events (> 10K tokens per event)
SELECT
  event_id,
  session_id,
  author,
  attestation.agent_name,
  annotations.input_tokens,
  annotations.output_tokens,
  (COALESCE(annotations.input_tokens, 0) + COALESCE(annotations.output_tokens, 0)) AS total_tokens,
  event_ts
FROM `pyagents.session_events_log`
WHERE (COALESCE(annotations.input_tokens, 0) + COALESCE(annotations.output_tokens, 0)) > 10000
  AND event_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
ORDER BY total_tokens DESC
LIMIT 20;

-- CHALLENGE: Find the event with the lowest behavioral score in YOUR session.
--            Why was it low? What would a higher score require?
