-- =============================================================================
-- LAB 1 — Query 6: Deep Inspection
-- =============================================================================
-- SCENARIO: "Agent spent $4,200 at 3am. CISO wants proof."
-- STEP: Extract the full attestation evidence for independent verification.
--
-- WHAT TO LOOK FOR:
--   - hash_digest: the SHA-256 content hash (L1)
--   - cert_fingerprint: identifies the KMS signing key (L2)
--   - evidence_version: attestation schema version
--   - spiffe_id + slsa_level: supply chain binding
--   - event_payload: the full event data (can be sent to /api/attestation/verify)
--
-- FINAL STEP: Copy the attestation evidence and POST to /api/attestation/verify
--   Response: { "verified": true, "chain_intact": true }
--   No shared backend. Evidence is self-contained and self-proving.
--
-- TABLE: pyagents.session_events_log
-- =============================================================================

SELECT
  event_id,
  author,
  attestation.valid AS attest_status,
  attestation.evidence_version,
  attestation.hash_digest,
  attestation.cert_fingerprint,
  attestation.has_sensitive_claims,
  attestation.spiffe_id,
  attestation.slsa_level,
  attestation.agent_name,
  attestation.model_id,
  attestation.tools_invoked,
  event_payload,
  event_ts
FROM `pyagents.session_events_log`
WHERE session_id = @session_id
  AND attestation.valid = 'SIGNATURE_OK'
ORDER BY event_ts ASC
LIMIT 5;

-- EXAMPLE PARAMETERS:
--   @session_id = 'sess_x7k9m2'  (from Query 1)
--
-- NEXT STEP: Take the event_payload from any row and POST to:
--   POST /api/attestation/verify
--   Body: { event_payload, hash_digest, cert_fingerprint }
--   Expected: { "verified": true, "chain_intact": true }
--
-- KEY POINT: The verifier has NO shared backend state with the attestor.
--            This is the difference between "trust us" and "watch this".
