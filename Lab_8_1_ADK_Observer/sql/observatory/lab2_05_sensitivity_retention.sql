-- =============================================================================
-- LAB 2 — Query 5: Sensitivity & Retention
-- =============================================================================
-- Which sessions held something sensitive, whether the persisted copy was scrubbed, and when the operational
-- (Firestore) copy is scheduled to disappear — the ledger keeps the record either way.
--
-- WHAT TO LOOK FOR:
--   - Sensitive sessions (5a/5b): a 'credential_secret' taint = a credential answer carried a secret. A SENSITIVITY
--     marker, not the integrity taint (tampering — Lab 2 Query 3). Trend it per app before tightening the scrub.
--   - Exposure vs scrub (5c/5d): in observe mode every exposure is persisted as sent (the soak metric); in enforce
--     mode declared_but_raw MUST be 0 — anything else means the archive kept a secret the event says was scrubbed.
--   - Planned expiry (5e): sessions the operational store will delete under native TTL — investigate BEFORE then.
--
-- TABLES: pyagents.session_ledger (annotations_extra, expires_at) · pyagents.session_events_log (event_payload)
-- =============================================================================

-- 5a. Sensitive sessions — latest ledger snapshot per session that carries any sensitivity taint (last 30d)
SELECT
  session_id,
  user_id,
  app_name,
  JSON_VALUE_ARRAY(annotations_extra, '$.sensitivity_taints') AS sensitivity_taints,
  CAST(JSON_VALUE(annotations_extra, '$.sensitive_event_count') AS INT64) AS sensitive_event_count,
  annotations.event_count,
  session_status,
  last_event_ts
FROM `pyagents.session_ledger`
WHERE recorded_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND JSON_QUERY(annotations_extra, '$.sensitivity_taints') IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY session_id ORDER BY recorded_at DESC) = 1
ORDER BY last_event_ts DESC
LIMIT 100;

-- 5b. Sensitivity rollup — sensitive sessions per day × app × taint (the observe-soak trend, last 30d)
WITH latest AS (
  SELECT session_id, app_name, annotations_extra, DATE(last_event_ts) AS day
  FROM `pyagents.session_ledger`
  WHERE recorded_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
    AND JSON_QUERY(annotations_extra, '$.sensitivity_taints') IS NOT NULL
  QUALIFY ROW_NUMBER() OVER (PARTITION BY session_id ORDER BY recorded_at DESC) = 1
)
SELECT
  day,
  app_name,
  taint,
  COUNT(DISTINCT session_id) AS sensitive_sessions
FROM latest, UNNEST(JSON_VALUE_ARRAY(annotations_extra, '$.sensitivity_taints')) AS taint
GROUP BY day, app_name, taint
ORDER BY day DESC, sensitive_sessions DESC;

-- 5c. Sensitive events for a session — which events, which taint, which fields (PATHS, never values), scrubbed?
SELECT
  event_id,
  author,
  invocation_id,
  event_ts,
  JSON_VALUE_ARRAY(event_payload, '$.custom_metadata.event_metadata.sensitivity.taints') AS taints,
  JSON_VALUE_ARRAY(event_payload,
    '$.custom_metadata.event_metadata.sensitivity.detail.credential_secret.fields') AS credential_secret_fields,
  JSON_VALUE(event_payload,
    '$.custom_metadata.event_metadata.sensitivity.detail.credential_secret.scrubbed') AS scrubbed,
  JSON_VALUE(event_payload,
    '$.custom_metadata.event_metadata.sensitivity.detail.credential_secret.source') AS source
FROM `pyagents.session_events_log`
WHERE session_id = '<SESSION_ID>'
  AND JSON_QUERY(event_payload, '$.custom_metadata.event_metadata.sensitivity') IS NOT NULL
ORDER BY event_ts ASC;

-- 5d. Scrub-mode conformance — credential_secret events per day: declared scrubbed vs not, and the persisted copy's
--     truth. observe ⇒ unscrubbed_exposures is the soak metric; enforce ⇒ declared_but_raw MUST be 0 (a non-zero row
--     means the archive kept a secret the event says was scrubbed — investigate before trusting the flip). Last 30d.
SELECT
  DATE(event_ts) AS day,
  app_name,
  COUNT(*) AS credential_secret_events,
  COUNTIF(JSON_VALUE(event_payload,
    '$.custom_metadata.event_metadata.sensitivity.detail.credential_secret.scrubbed') = 'false') AS unscrubbed_exposures,
  COUNTIF(JSON_VALUE(event_payload,
    '$.custom_metadata.event_metadata.sensitivity.detail.credential_secret.scrubbed') = 'true') AS declared_scrubbed,
  COUNTIF(JSON_VALUE(event_payload,
            '$.custom_metadata.event_metadata.sensitivity.detail.credential_secret.scrubbed') = 'true'
          AND NOT CONTAINS_SUBSTR(TO_JSON_STRING(event_payload), '[scrubbed:td376:')) AS declared_but_raw
FROM `pyagents.session_events_log`
WHERE event_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND 'credential_secret' IN UNNEST(
        JSON_VALUE_ARRAY(event_payload, '$.custom_metadata.event_metadata.sensitivity.taints'))
GROUP BY day, app_name
ORDER BY day DESC;

-- 5e. Planned operational expiry (TD-369) — sessions whose Firestore copy is scheduled for native-TTL deletion,
--     by expiry day (latest snapshot per session). The ledger keeps the record; Firestore deletes silently.
--     NULL expires_at = no retention (TTL not promoted in this env, or an interactive session under a 0-day policy).
WITH latest AS (
  SELECT session_id, app_name, expires_at, annotations.event_count AS event_count, last_event_ts
  FROM `pyagents.session_ledger`
  WHERE expires_at IS NOT NULL
  QUALIFY ROW_NUMBER() OVER (PARTITION BY session_id ORDER BY recorded_at DESC) = 1
)
SELECT
  DATE(expires_at) AS expires_on,
  app_name,
  COUNT(*) AS sessions,
  SUM(event_count) AS events,
  MIN(last_event_ts) AS oldest_last_activity
FROM latest
WHERE expires_at <= TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY expires_on, app_name
ORDER BY expires_on ASC;
