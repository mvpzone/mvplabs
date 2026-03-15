-- =============================================================================
-- LAB 1 — Query 3: Mandate Verification
-- =============================================================================
-- SCENARIO: "Agent spent $4,200 at 3am. CISO wants proof."
-- STEP: Verify the mandate that authorized the spend — was it valid? In scope?
--
-- WHAT TO LOOK FOR:
--   - mandate_status: should be ACTIVE (not REVOKED or EXPIRED)
--   - signing_scope: links the mandate to the originating session
--   - policy_tier: shows the governance level (user, team, platform)
--   - cumulative_uom_value: the total spend against this mandate
--   - Compare cumulative spend vs spend ceiling (from mandate_payload)
--
-- TABLE: pyagents.mandate_ledger
-- CROSS-TABLE: signing_scope links mandate_ledger to session_events_log
-- =============================================================================

SELECT
  mandate_id,
  mandate_type,
  mandate_domain,
  mandate_status,
  annotations.signing_scope,
  annotations.policy_tier,
  annotations.delegation_type,
  annotations.cumulative_uom_value,
  annotations.total_executions,
  signed_at,
  expires_at,
  constraint_fingerprint
FROM `pyagents.mandate_ledger`
WHERE annotations.signing_scope LIKE CONCAT('%', @session_id_fragment, '%')
ORDER BY signed_at DESC;

-- EXAMPLE PARAMETERS:
--   @session_id_fragment = 'sess_original'  (or partial session ID from the originating session)
--
-- EXPECTED: Mandate im_r4s5t6 — signed by user, ES256, $5,000 ceiling, ACTIVE.
--           $4,200 < $5,000 = COMPLIANT.
