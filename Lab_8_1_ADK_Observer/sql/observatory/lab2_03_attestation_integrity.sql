-- =============================================================================
-- LAB 2 — Query 3: Attestation Integrity
-- =============================================================================
-- L1/L2/L3 attestation status across all events in the last 24 hours.
--
-- WHAT TO LOOK FOR:
--   - verify_pct: should be 100% (all signed events verify correctly)
--   - tainted: should be 0 (monotonic — once set, never cleared)
--   - l3_events: events with encrypted attestation (sensitive data)
--   - Any SIGNATURE_TAINTED events require immediate investigation
--
-- TABLE: pyagents.session_events_log
-- =============================================================================

-- 3a. Daily attestation coverage
SELECT
  DATE(event_ts) AS day,
  COUNT(*) AS total_events,
  COUNTIF(attestation.valid = 'SIGNATURE_OK') AS verified,
  COUNTIF(attestation.valid = 'SIGNATURE_TAINTED') AS tainted,
  COUNTIF(attestation.valid = 'SIGNATURE_NA') AS unsigned,
  COUNTIF(attestation.has_sensitive_claims = TRUE) AS l3_events,
  ROUND(
    SAFE_DIVIDE(
      COUNTIF(attestation.valid = 'SIGNATURE_OK'),
      COUNTIF(attestation.valid IS NOT NULL)
    ) * 100, 1
  ) AS verify_pct
FROM `pyagents.session_events_log`
WHERE event_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY day
ORDER BY day DESC;

-- 3b. Per-agent attestation status
SELECT
  attestation.agent_name,
  COUNT(*) AS events,
  COUNTIF(attestation.valid = 'SIGNATURE_OK') AS verified,
  COUNTIF(attestation.valid = 'SIGNATURE_TAINTED') AS tainted,
  COUNTIF(attestation.has_sensitive_claims = TRUE) AS l3_events,
  attestation.evidence_version
FROM `pyagents.session_events_log`
WHERE attestation.valid IS NOT NULL
  AND event_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY attestation.agent_name, attestation.evidence_version
ORDER BY events DESC;

-- KEY INSIGHT: L1 = hash (tamper detection), L2 = signed (non-repudiation),
--              L3 = sealed (privacy + soft revocation via Secret Manager rotation)
