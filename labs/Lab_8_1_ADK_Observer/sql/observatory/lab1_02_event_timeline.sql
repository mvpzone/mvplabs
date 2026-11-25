-- =============================================================================
-- LAB 1 — Query 2: Event Timeline
-- =============================================================================
-- SCENARIO: "Agent spent $4,200 at 3am. CISO wants proof."
-- STEP: Trace the full event sequence — who did what, when.
--
-- WHAT TO LOOK FOR:
--   - author column shows the delegation chain (user → maestro → specialist agents)
--   - attestation.valid confirms every event is signed (SIGNATURE_OK)
--   - tools_invoked shows what actions each agent took
--   - The event sequence tells the story of the autonomous execution
--
-- TABLE: pyagents.session_events_log
-- =============================================================================

SELECT
  event_id,
  author,
  attestation.agent_name,
  attestation.valid AS attest_status,
  attestation.tools_invoked,
  annotations.input_tokens,
  annotations.output_tokens,
  event_ts
FROM `pyagents.session_events_log`
WHERE session_id = @session_id
ORDER BY event_ts ASC;

-- EXAMPLE PARAMETERS:
--   @session_id = 'sess_x7k9m2'  (from Query 1)
--
-- EXPECTED: Full delegation chain — Shopping → InventoryAnalyst → ReorderPipeline
