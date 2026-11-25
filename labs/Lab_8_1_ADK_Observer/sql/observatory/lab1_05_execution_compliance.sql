-- =============================================================================
-- LAB 1 — Query 5: Execution Compliance
-- =============================================================================
-- SCENARIO: "Agent spent $4,200 at 3am. CISO wants proof."
-- STEP: Check each execution against the mandate — was every action compliant?
--
-- WHAT TO LOOK FOR:
--   - outcome: SUCCESS / FAILURE / ERROR
--   - compliance_status: COMPLIANT / VIOLATION / PENDING
--   - uom_value: the spend for this specific execution
--   - duration_ms: execution time (compare against baseline for anomalies)
--   - decision_step_count: how many decision steps the agent took
--
-- TABLE: pyagents.mandate_executions_log
-- =============================================================================

SELECT
  execution_id,
  mandate_id,
  annotations.execution_state,
  annotations.outcome,
  annotations.compliance_status,
  annotations.trigger_reason,
  annotations.uom_value,
  annotations.duration_ms,
  annotations.decision_step_count,
  triggered_at,
  completed_at
FROM `pyagents.mandate_executions_log`
WHERE mandate_id = @mandate_id
ORDER BY triggered_at ASC;

-- EXAMPLE PARAMETERS:
--   @mandate_id = 'im_r4s5t6'  (from Query 3)
--
-- EXPECTED: All executions COMPLIANT. Duration, token consumption, and tool calls
--           within baseline. Verdict: NORMAL — no anomalous behavior.
