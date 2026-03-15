-- =============================================================================
-- LAB 2 — Query 4: Token Timeline
-- =============================================================================
-- Token volume over time — detect spikes that may indicate anomalous behavior.
--
-- WHAT TO LOOK FOR:
--   - Spikes in token volume: potential prompt injection or data exfiltration
--   - After-hours activity: events outside expected business hours
--   - Sustained high volume: slow-burn attacks (credential abuse, drift)
--   - Compare per-hour patterns to establish a behavioral baseline
--
-- TABLE: pyagents.session_events_log
-- =============================================================================

-- 4a. Hourly token volume (last 24h)
SELECT
  TIMESTAMP_TRUNC(event_ts, HOUR) AS hour,
  COUNT(*) AS events,
  COUNT(DISTINCT session_id) AS sessions,
  SUM(COALESCE(annotations.input_tokens, 0)) AS input_tokens,
  SUM(COALESCE(annotations.output_tokens, 0)) AS output_tokens,
  SUM(COALESCE(annotations.input_tokens, 0) + COALESCE(annotations.output_tokens, 0)) AS total_tokens
FROM `pyagents.session_events_log`
WHERE event_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY hour
ORDER BY hour ASC;

-- 4b. Per-session token consumption (ranked)
SELECT
  session_id,
  user_id,
  COUNT(*) AS events,
  SUM(COALESCE(annotations.input_tokens, 0)) AS input_tokens,
  SUM(COALESCE(annotations.output_tokens, 0)) AS output_tokens,
  SUM(COALESCE(annotations.input_tokens, 0) + COALESCE(annotations.output_tokens, 0)) AS total_tokens,
  MIN(event_ts) AS first_event,
  MAX(event_ts) AS last_event
FROM `pyagents.session_events_log`
WHERE event_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY session_id, user_id
ORDER BY total_tokens DESC
LIMIT 20;

-- KEY INSIGHT: "45 forensic queries on live session data.
--               This is what your SOX auditor wants to see."
