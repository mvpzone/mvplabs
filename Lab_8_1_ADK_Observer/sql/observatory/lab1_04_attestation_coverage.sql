-- =============================================================================
-- LAB 1 — Query 4: Attestation Coverage
-- =============================================================================
-- SCENARIO: "Agent spent $4,200 at 3am. CISO wants proof."
-- STEP: Verify attestation integrity — are ALL events signed? Any tainted?
--
-- WHAT TO LOOK FOR:
--   - total vs verified: should be equal (100% coverage)
--   - tainted: should be 0 (no integrity violations)
--   - SIGNATURE_OK means the KMS signature verified correctly
--   - SIGNATURE_TAINTED means the event was modified after signing (monotonic — never clears)
--
-- TABLE: pyagents.session_events_log
-- =============================================================================

SELECT
  COUNT(*) AS total_events,
  COUNTIF(attestation.valid IS NOT NULL) AS attested,
  COUNTIF(attestation.valid = 'SIGNATURE_OK') AS verified,
  COUNTIF(attestation.valid = 'SIGNATURE_TAINTED') AS tainted,
  COUNTIF(attestation.valid = 'SIGNATURE_NA') AS unsigned,
  ROUND(
    SAFE_DIVIDE(
      COUNTIF(attestation.valid = 'SIGNATURE_OK'),
      COUNTIF(attestation.valid IS NOT NULL)
    ) * 100, 1
  ) AS verify_pct
FROM `pyagents.session_events_log`
WHERE session_id = @session_id;

-- EXAMPLE PARAMETERS:
--   @session_id = 'sess_x7k9m2'  (from Query 1)
--
-- EXPECTED: 24/24 SIGNATURE_OK, 0 tainted, 100% verify rate.
--           Chain unbroken. No tampering detected.
