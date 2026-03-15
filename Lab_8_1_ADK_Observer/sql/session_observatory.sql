-- =============================================================================
-- Session Forensics — BQ Queries for pyagents.session_events_log + session_ledger
-- =============================================================================
-- Tables:
--   pyagents.session_events_log  (per-event, partition: event_ts, cluster: app_name, user_id, session_id)
--   pyagents.session_ledger      (lifecycle, partition: created_at, cluster: app_name, user_id, session_id)
--
-- Replace PROJECT with: ts-prot-npp-ai-sec-dev | ts-canvas-dev | ts-no-prot-npp-ai-sec-dev
-- =============================================================================


-- ═══════════════════════════════════════════════════════════════════════
-- 0. QUICK VALIDATION — Verify BQ pipeline is working
-- ═══════════════════════════════════════════════════════════════════════

-- 0a. Per-event token annotations for a session
SELECT
  event_id,
  author,
  invocation_id,
  source_id,
  annotations.input_tokens,
  annotations.output_tokens,
  annotations.total_tokens,
  event_ts
FROM `pyagents.session_events_log`
WHERE session_id = '<SESSION_ID>'
ORDER BY event_ts;

-- 0b. Ledger cumulative progression for a session
SELECT
  session_id,
  session_status,
  annotations.event_count,
  annotations.invocation_count,
  annotations.input_tokens,
  annotations.output_tokens,
  annotations.attestation_count,
  source_id,
  created_at,
  last_event_ts,
  recorded_at
FROM `pyagents.session_ledger`
WHERE session_id = '<SESSION_ID>'
ORDER BY recorded_at;

-- 0c. Row counts (sanity check)
SELECT 'events_log' AS tbl, COUNT(*) AS rows FROM `pyagents.session_events_log`
UNION ALL
SELECT 'ledger', COUNT(*) FROM `pyagents.session_ledger`;

-- 0d. Source instance distribution (verify source_id populated)
SELECT
  source_id,
  COUNT(*) AS events,
  COUNT(DISTINCT session_id) AS sessions,
  MIN(event_ts) AS first_seen,
  MAX(event_ts) AS last_seen
FROM `pyagents.session_events_log`
WHERE event_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY source_id
ORDER BY events DESC;


-- ═══════════════════════════════════════════════════════════════════════
-- 1. SESSION INVENTORY
-- ═══════════════════════════════════════════════════════════════════════

-- 1a. Recent sessions (last 24h)
SELECT
  session_id,
  app_name,
  user_id,
  session_status,
  source_id,
  annotations.event_count,
  annotations.invocation_count,
  annotations.input_tokens,
  annotations.output_tokens,
  created_at,
  last_event_ts,
  duration_seconds
FROM `pyagents.session_ledger`
WHERE session_status = 'active'
  AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
ORDER BY created_at DESC;

-- 1b. Session volume by user (last 7 days)
SELECT
  user_id,
  COUNT(DISTINCT session_id) AS sessions,
  SUM(annotations.event_count) AS total_events,
  SUM(annotations.input_tokens) AS total_input_tokens,
  SUM(annotations.output_tokens) AS total_output_tokens
FROM `pyagents.session_ledger`
WHERE session_status = 'active'
  AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY user_id
ORDER BY sessions DESC;

-- 1c. Session volume by app (last 7 days)
SELECT
  app_name,
  COUNT(DISTINCT session_id) AS sessions,
  SUM(annotations.event_count) AS total_events,
  ROUND(AVG(duration_seconds), 1) AS avg_duration_secs
FROM `pyagents.session_ledger`
WHERE session_status = 'active'
  AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY app_name
ORDER BY sessions DESC;

-- 1d. Multi-agent sessions — sessions with agent delegation chains
SELECT
  session_id,
  user_id,
  app_name,
  annotations.agent_counts,
  annotations.tool_counts,
  annotations.event_count,
  annotations.invocation_count,
  annotations.attestation_count,
  annotations.verified_count,
  ROUND(duration_seconds / 60, 1) AS duration_min,
  created_at
FROM `pyagents.session_ledger`
WHERE session_status = 'active'
  AND JSON_VALUE(annotations.tool_counts, '$.transfer_to_agent') IS NOT NULL
  AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
ORDER BY created_at DESC;

-- 1e. Agent delegation trace for a session — event-level agent handoffs
SELECT
  event_id,
  author,
  attestation.agent_name AS attesting_agent,
  attestation.tools_invoked,
  CASE
    WHEN 'transfer_to_agent' IN UNNEST(attestation.tools_invoked) THEN 'HANDOFF'
    WHEN attestation.tools_invoked IS NOT NULL AND ARRAY_LENGTH(attestation.tools_invoked) > 0 THEN 'TOOL_CALL'
    WHEN annotations.input_tokens IS NOT NULL THEN 'MODEL'
    ELSE 'LIFECYCLE'
  END AS event_role,
  annotations.input_tokens,
  annotations.output_tokens,
  event_ts
FROM `pyagents.session_events_log`
WHERE session_id = '<SESSION_ID>'
ORDER BY event_ts ASC;


-- ═══════════════════════════════════════════════════════════════════════
-- 2. EVENT DRILL-DOWN
-- ═══════════════════════════════════════════════════════════════════════

-- 2a. Event timeline for a specific session
SELECT
  event_id,
  author,
  invocation_id,
  event_ts,
  attestation.valid AS attest_status,
  attestation.agent_name,
  attestation.model_id,
  attestation.tools_invoked,
  annotations.input_tokens,
  annotations.output_tokens,
  annotations.is_flagged
FROM `pyagents.session_events_log`
WHERE session_id = '<SESSION_ID>'
ORDER BY event_ts ASC;

-- 2b. Events with attestation details
SELECT
  event_id,
  author,
  event_ts,
  attestation.valid AS attest_status,
  attestation.evidence_version,
  attestation.hash_digest,
  attestation.cert_fingerprint,
  attestation.has_sensitive_claims,
  attestation.spiffe_id,
  attestation.slsa_level
FROM `pyagents.session_events_log`
WHERE session_id = '<SESSION_ID>'
  AND attestation.valid IS NOT NULL
ORDER BY event_ts ASC;

-- 2c. Tool usage in a session
SELECT
  event_id,
  author,
  event_ts,
  tool
FROM `pyagents.session_events_log`,
  UNNEST(attestation.tools_invoked) AS tool
WHERE session_id = '<SESSION_ID>'
ORDER BY event_ts ASC;

-- 2d. Tool delegation flow — shows agent→tool→response event pattern
SELECT
  event_id,
  author,
  attestation.valid AS attest_status,
  attestation.tools_invoked,
  annotations.input_tokens,
  annotations.output_tokens,
  CASE
    WHEN ARRAY_LENGTH(attestation.tools_invoked) > 0 AND annotations.input_tokens IS NOT NULL THEN 'delegate'
    WHEN ARRAY_LENGTH(attestation.tools_invoked) > 0 AND annotations.input_tokens IS NULL THEN 'tool_response'
    WHEN annotations.input_tokens IS NOT NULL THEN 'model_response'
    WHEN author = 'user' THEN 'user_input'
    ELSE 'lifecycle'
  END AS event_type,
  event_ts
FROM `pyagents.session_events_log`
WHERE session_id = '<SESSION_ID>'
ORDER BY event_ts ASC;


-- ═══════════════════════════════════════════════════════════════════════
-- 2.5. INVOCATION-LEVEL ANALYSIS
-- ═══════════════════════════════════════════════════════════════════════

-- 2.5a. Per-invocation summary for a session (token usage per turn)
SELECT
  invocation_id,
  COUNT(*) AS events,
  MIN(event_ts) AS started,
  MAX(event_ts) AS ended,
  TIMESTAMP_DIFF(MAX(event_ts), MIN(event_ts), SECOND) AS duration_secs,
  SUM(annotations.input_tokens) AS input_tokens,
  SUM(annotations.output_tokens) AS output_tokens,
  ARRAY_AGG(DISTINCT author IGNORE NULLS) AS authors,
  COUNTIF(attestation.valid IS NOT NULL) AS attested_events
FROM `pyagents.session_events_log`
WHERE session_id = '<SESSION_ID>'
GROUP BY invocation_id
ORDER BY started ASC;

-- 2.5b. Per-invocation tool calls for a session
SELECT
  invocation_id,
  ARRAY_AGG(DISTINCT tool) AS tools_used,
  COUNT(tool) AS tool_calls,
  MIN(event_ts) AS first_event
FROM `pyagents.session_events_log`,
  UNNEST(attestation.tools_invoked) AS tool
WHERE session_id = '<SESSION_ID>'
GROUP BY invocation_id
ORDER BY first_event ASC;

-- 2.5c. Invocation cost ranking (top invocations by token consumption, last 7d)
SELECT
  session_id,
  invocation_id,
  COUNT(*) AS events,
  SUM(annotations.input_tokens) AS input_tokens,
  SUM(annotations.output_tokens) AS output_tokens,
  SUM(COALESCE(annotations.input_tokens, 0) + COALESCE(annotations.output_tokens, 0)) AS total_tokens
FROM `pyagents.session_events_log`
WHERE event_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY session_id, invocation_id
ORDER BY total_tokens DESC
LIMIT 50;

-- 2.5d. Invocation forensics — combined agent chain + tools per invocation (reverse hunt)
SELECT
  invocation_id,
  COUNT(*) AS events,
  MIN(event_ts) AS started,
  MAX(event_ts) AS ended,
  TIMESTAMP_DIFF(MAX(event_ts), MIN(event_ts), SECOND) AS duration_secs,
  SUM(annotations.input_tokens) AS input_tokens,
  SUM(annotations.output_tokens) AS output_tokens,
  ARRAY_AGG(DISTINCT author IGNORE NULLS) AS agents,
  ARRAY_AGG(DISTINCT tool IGNORE NULLS) AS tools_used,
  COUNTIF(attestation.valid = 'SIGNATURE_OK') AS verified,
  COUNTIF(attestation.has_sensitive_claims = TRUE) AS l3_events
FROM `pyagents.session_events_log`
  LEFT JOIN UNNEST(attestation.tools_invoked) AS tool
WHERE session_id = '<SESSION_ID>'
GROUP BY invocation_id
ORDER BY started ASC;


-- ═══════════════════════════════════════════════════════════════════════
-- 3. TRUST & SAFETY FORENSICS
-- ═══════════════════════════════════════════════════════════════════════

-- 3a. Flagged sessions
SELECT
  session_id,
  user_id,
  app_name,
  annotations.flagged_count,
  annotations.flag_types,
  annotations.first_flagged_event_id,
  annotations.event_count,
  created_at
FROM `pyagents.session_ledger`
WHERE annotations.flagged_count > 0
ORDER BY created_at DESC
LIMIT 50;

-- 3b. Flagged events detail
SELECT
  e.event_id,
  e.session_id,
  e.user_id,
  e.author,
  e.event_ts,
  e.annotations.flag_types,
  e.attestation.agent_name,
  e.attestation.model_id
FROM `pyagents.session_events_log` e
WHERE e.annotations.is_flagged = TRUE
ORDER BY e.event_ts DESC
LIMIT 100;

-- 3c. Tainted sessions (attestation integrity violations)
SELECT
  session_id,
  user_id,
  app_name,
  annotations.tainted_count,
  annotations.first_tainted_event_id,
  annotations.attestation_count,
  annotations.verified_count,
  created_at
FROM `pyagents.session_ledger`
WHERE annotations.is_tainted = TRUE
ORDER BY created_at DESC;

-- 3d. Sessions with high token consumption (anomaly detection)
SELECT
  session_id,
  user_id,
  app_name,
  annotations.input_tokens,
  annotations.output_tokens,
  (annotations.input_tokens + annotations.output_tokens) AS total_tokens,
  annotations.event_count,
  duration_seconds
FROM `pyagents.session_ledger`
WHERE session_status = 'active'
  AND (annotations.input_tokens + annotations.output_tokens) > 100000
ORDER BY total_tokens DESC
LIMIT 50;


-- 3e. Duplicate event detection (same event_id inserted multiple times)
SELECT
  event_id,
  session_id,
  author,
  COUNT(*) AS dupes
FROM `pyagents.session_events_log`
WHERE event_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY event_id, session_id, author
HAVING COUNT(*) > 1
ORDER BY dupes DESC;

-- 3f. Duplicate event detail for a session
SELECT
  event_id,
  author,
  attestation.valid AS attest_status,
  attestation.tools_invoked,
  annotations.input_tokens,
  event_ts
FROM `pyagents.session_events_log`
WHERE session_id = '<SESSION_ID>'
  AND event_id IN (
    SELECT event_id
    FROM `pyagents.session_events_log`
    WHERE session_id = '<SESSION_ID>'
    GROUP BY event_id
    HAVING COUNT(*) > 1
  )
ORDER BY event_ts, event_id;

-- 3g. Attestation counter discrepancy — ledger vs events
SELECT
  l.session_id,
  l.annotations.attestation_count AS ledger_attest_count,
  l.annotations.verified_count AS ledger_verified,
  e.actual_attested,
  e.actual_verified
FROM `pyagents.session_ledger` l
LEFT JOIN (
  SELECT
    session_id,
    COUNTIF(attestation.valid IS NOT NULL) AS actual_attested,
    COUNTIF(attestation.valid = 'SIGNATURE_OK') AS actual_verified
  FROM `pyagents.session_events_log`
  GROUP BY session_id
) e ON l.session_id = e.session_id
WHERE l.session_status = 'active'
  AND (l.annotations.attestation_count != e.actual_attested
       OR l.annotations.verified_count != e.actual_verified)
ORDER BY l.created_at DESC;

-- 3h. HITL sessions — sessions that triggered user confirmation prompts
SELECT
  session_id,
  user_id,
  app_name,
  annotations.tool_counts,
  annotations.event_count,
  annotations.invocation_count,
  created_at,
  last_event_ts
FROM `pyagents.session_ledger`
WHERE session_status = 'active'
  AND JSON_VALUE(annotations.tool_counts, '$.adk_request_confirmation') IS NOT NULL
  AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
ORDER BY created_at DESC;

-- 3i. Auth/credential sessions — sessions that triggered OAuth consent flows
SELECT
  session_id,
  user_id,
  app_name,
  annotations.tool_counts,
  annotations.agent_counts,
  annotations.event_count,
  created_at,
  last_event_ts
FROM `pyagents.session_ledger`
WHERE session_status = 'active'
  AND JSON_VALUE(annotations.tool_counts, '$.adk_request_credential') IS NOT NULL
  AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
ORDER BY created_at DESC;


-- ═══════════════════════════════════════════════════════════════════════
-- 4. ATTESTATION ANALYTICS
-- ═══════════════════════════════════════════════════════════════════════

-- 4a. Attestation coverage (what % of events are signed?)
SELECT
  DATE(event_ts) AS day,
  COUNT(*) AS total_events,
  COUNTIF(attestation.valid IS NOT NULL) AS attested_events,
  COUNTIF(attestation.valid = 'SIGNATURE_OK') AS verified,
  COUNTIF(attestation.valid = 'SIGNATURE_NA') AS unsigned,
  COUNTIF(attestation.valid = 'SIGNATURE_TAINTED') AS tainted,
  ROUND(SAFE_DIVIDE(COUNTIF(attestation.valid = 'SIGNATURE_OK'), COUNTIF(attestation.valid IS NOT NULL)) * 100, 1) AS verify_pct
FROM `pyagents.session_events_log`
WHERE event_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY day
ORDER BY day DESC;

-- 4b. Attestation by agent
SELECT
  attestation.agent_name,
  attestation.evidence_version,
  COUNT(*) AS events,
  COUNTIF(attestation.valid = 'SIGNATURE_OK') AS verified,
  COUNTIF(attestation.valid = 'SIGNATURE_TAINTED') AS tainted
FROM `pyagents.session_events_log`
WHERE attestation.valid IS NOT NULL
  AND event_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY attestation.agent_name, attestation.evidence_version
ORDER BY events DESC;

-- 4c. Sessions with full attestation coverage
SELECT
  session_id,
  user_id,
  annotations.attestation_count,
  annotations.verified_count,
  annotations.all_producers_verified
FROM `pyagents.session_ledger`
WHERE session_status = 'active'
  AND annotations.all_producers_verified = TRUE
ORDER BY created_at DESC
LIMIT 50;

-- 4d. L3 sensitive claims events (encrypted attestation — OAuth/PII tools)
SELECT
  event_id,
  session_id,
  author,
  attestation.valid AS attest_status,
  attestation.agent_name,
  attestation.has_sensitive_claims,
  attestation.tools_invoked,
  annotations.input_tokens,
  annotations.output_tokens,
  event_ts
FROM `pyagents.session_events_log`
WHERE attestation.has_sensitive_claims = TRUE
  AND event_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
ORDER BY event_ts DESC
LIMIT 100;

-- 4e. L3 coverage by agent — which agents handle sensitive data?
SELECT
  attestation.agent_name,
  COUNT(*) AS l3_events,
  COUNTIF(attestation.valid = 'SIGNATURE_OK') AS verified,
  COUNT(DISTINCT session_id) AS sessions,
  ARRAY_AGG(DISTINCT tool IGNORE NULLS) AS sensitive_tools
FROM `pyagents.session_events_log`,
  UNNEST(attestation.tools_invoked) AS tool
WHERE attestation.has_sensitive_claims = TRUE
  AND event_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY attestation.agent_name
ORDER BY l3_events DESC;


-- ═══════════════════════════════════════════════════════════════════════
-- 5. OPERATIONAL METRICS
-- ═══════════════════════════════════════════════════════════════════════

-- 5a. Daily usage summary
SELECT
  DATE(created_at) AS day,
  COUNT(DISTINCT session_id) AS sessions,
  COUNT(DISTINCT user_id) AS unique_users,
  SUM(annotations.event_count) AS total_events,
  SUM(annotations.input_tokens) AS total_input_tokens,
  SUM(annotations.output_tokens) AS total_output_tokens,
  ROUND(AVG(duration_seconds), 1) AS avg_session_duration
FROM `pyagents.session_ledger`
WHERE session_status = 'active'
  AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY day
ORDER BY day DESC;

-- 5b. Tool popularity (from events — per-event tool_invoked via attestation)
SELECT
  tool,
  COUNT(*) AS invocations,
  COUNT(DISTINCT session_id) AS sessions
FROM `pyagents.session_events_log`,
  UNNEST(attestation.tools_invoked) AS tool
WHERE event_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY tool
ORDER BY invocations DESC
LIMIT 30;

-- 5c. Tool popularity (from ledger — session-level tool_counts map)
SELECT
  session_id,
  user_id,
  annotations.tool_counts AS tool_counts_json,
  annotations.event_count,
  created_at
FROM `pyagents.session_ledger`
WHERE session_status = 'active'
  AND annotations.tool_counts != '{}'
  AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
ORDER BY created_at DESC;

-- 5d. Agent distribution (from ledger — session-level agent_counts map)
SELECT
  session_id,
  user_id,
  annotations.agent_counts AS agent_counts_json,
  annotations.invocation_count,
  annotations.event_count,
  created_at
FROM `pyagents.session_ledger`
WHERE session_status = 'active'
  AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
ORDER BY created_at DESC;

-- 5e. Model usage distribution (from events)
SELECT
  attestation.model_id,
  COUNT(*) AS events,
  COUNT(DISTINCT session_id) AS sessions
FROM `pyagents.session_events_log`
WHERE attestation.model_id IS NOT NULL
  AND event_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY attestation.model_id
ORDER BY events DESC;

-- 5f. Agent distribution (from events)
SELECT
  attestation.agent_name,
  COUNT(*) AS events,
  COUNT(DISTINCT session_id) AS sessions,
  COUNT(DISTINCT user_id) AS unique_users
FROM `pyagents.session_events_log`
WHERE attestation.agent_name IS NOT NULL
  AND event_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY attestation.agent_name
ORDER BY events DESC;

-- 5g. Source instance health — events per serving instance
SELECT
  source_id,
  COUNT(*) AS events,
  COUNT(DISTINCT session_id) AS sessions,
  COUNT(DISTINCT user_id) AS users,
  MIN(event_ts) AS first_event,
  MAX(event_ts) AS last_event
FROM `pyagents.session_events_log`
WHERE event_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY source_id
ORDER BY events DESC;

-- 5h. Flow type distribution — which orchestrated flows are being used?
SELECT
  CASE
    WHEN JSON_VALUE(annotations.agent_counts, '$.HaikuFlow') IS NOT NULL THEN 'Haiku'
    WHEN JSON_VALUE(annotations.agent_counts, '$.MediaFlow') IS NOT NULL THEN 'Media'
    WHEN JSON_VALUE(annotations.agent_counts, '$.DocsFlow') IS NOT NULL THEN 'Docs'
    WHEN JSON_VALUE(annotations.agent_counts, '$.TrustSafetyFlow') IS NOT NULL THEN 'TrustSafety'
    ELSE 'Simple'
  END AS flow_type,
  COUNT(DISTINCT session_id) AS sessions,
  SUM(annotations.event_count) AS total_events,
  SUM(annotations.input_tokens) AS total_input_tokens,
  SUM(annotations.output_tokens) AS total_output_tokens,
  ROUND(AVG(duration_seconds), 1) AS avg_duration_secs
FROM `pyagents.session_ledger`
WHERE session_status = 'active'
  AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY flow_type
ORDER BY sessions DESC;

-- 5i. Flow type per invocation — isolate individual flow runs across all sessions
SELECT
  session_id,
  invocation_id,
  CASE
    WHEN 'HaikuFlow' IN UNNEST(ARRAY_AGG(DISTINCT author)) THEN 'Haiku'
    WHEN 'MediaFlow' IN UNNEST(ARRAY_AGG(DISTINCT author)) THEN 'Media'
    WHEN 'DocsFlow' IN UNNEST(ARRAY_AGG(DISTINCT author)) THEN 'Docs'
    WHEN 'TrustSafetyFlow' IN UNNEST(ARRAY_AGG(DISTINCT author)) THEN 'TrustSafety'
    ELSE 'Simple'
  END AS flow_type,
  COUNT(*) AS events,
  TIMESTAMP_DIFF(MAX(event_ts), MIN(event_ts), SECOND) AS duration_secs,
  SUM(annotations.input_tokens) AS input_tokens,
  SUM(annotations.output_tokens) AS output_tokens,
  COUNTIF(attestation.has_sensitive_claims = TRUE) AS l3_events,
  COUNTIF(attestation.valid = 'SIGNATURE_OK') AS verified
FROM `pyagents.session_events_log`
WHERE event_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY session_id, invocation_id
ORDER BY MIN(event_ts) DESC
LIMIT 100;


-- ═══════════════════════════════════════════════════════════════════════
-- 6. SESSION LIFECYCLE
-- ═══════════════════════════════════════════════════════════════════════

-- 6a. Session lifecycle transitions
SELECT
  session_id,
  session_status,
  source_id,
  annotations.event_count,
  annotations.invocation_count,
  annotations.input_tokens,
  annotations.output_tokens,
  annotations.attestation_count,
  created_at,
  last_event_ts,
  recorded_at
FROM `pyagents.session_ledger`
WHERE session_id = '<SESSION_ID>'
ORDER BY recorded_at ASC;

-- 6b. Purged sessions
SELECT
  session_id,
  user_id,
  app_name,
  annotations.event_count,
  created_at,
  purged_at,
  duration_seconds
FROM `pyagents.session_ledger`
WHERE purged = TRUE
ORDER BY purged_at DESC
LIMIT 50;

-- 6c. Long-running sessions (> 30 minutes)
SELECT
  session_id,
  user_id,
  app_name,
  annotations.event_count,
  annotations.invocation_count,
  ROUND(duration_seconds / 60, 1) AS duration_minutes,
  created_at
FROM `pyagents.session_ledger`
WHERE session_status = 'active'
  AND duration_seconds > 1800
ORDER BY duration_seconds DESC
LIMIT 50;
