-- =============================================================================
-- LAB 2 — Query 1: Session Overview
-- =============================================================================
-- All sessions in the last 24 hours with trust scores and attestation status.
--
-- WHAT TO LOOK FOR:
--   - attestation_count vs verified_count: should match (100% coverage)
--   - is_tainted: any TRUE values indicate integrity violations
--   - all_producers_verified: TRUE = every agent in the session is attested
--   - event_count + duration: baseline for "normal" session behavior
--
-- TABLE: pyagents.session_ledger
-- =============================================================================

SELECT
  session_id,
  app_name,
  user_id,
  annotations.event_count,
  annotations.attestation_count,
  annotations.verified_count,
  annotations.tainted_count,
  annotations.is_tainted,
  annotations.all_producers_verified,
  ROUND(duration_seconds / 60, 1) AS duration_min,
  created_at
FROM `pyagents.session_ledger`
WHERE session_status = 'active'
  AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
ORDER BY created_at DESC;

-- EXPECTED: Multiple sessions. All should show is_tainted = FALSE and
--           all_producers_verified = TRUE. Any exceptions warrant investigation.
