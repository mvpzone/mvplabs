-- =============================================================================
-- LAB 1 — Query 1: Session Inventory
-- =============================================================================
-- SCENARIO: "Agent spent $4,200 at 3am. CISO wants proof."
-- STEP: Find the session by user and time range.
--
-- WHAT TO LOOK FOR:
--   - session_id to use in subsequent queries
--   - event_count and duration to gauge session scope
--   - app_name confirms the right application
--
-- TABLE: pyagents.session_ledger
-- =============================================================================

SELECT
  session_id,
  app_name,
  user_id,
  annotations.event_count,
  annotations.invocation_count,
  annotations.attestation_count,
  annotations.verified_count,
  duration_seconds,
  created_at,
  last_event_ts
FROM `pyagents.session_ledger`
WHERE user_id = @user_id
  AND created_at BETWEEN @start_time AND @end_time
ORDER BY created_at DESC;

-- EXAMPLE PARAMETERS:
--   @user_id   = 'agent-user@corp.google.com'
--   @start_time = '2026-03-17 02:00:00 UTC'
--   @end_time   = '2026-03-17 04:00:00 UTC'
--
-- EXPECTED: One session (e.g. sess_x7k9m2), 24 events, ~2m36s duration
