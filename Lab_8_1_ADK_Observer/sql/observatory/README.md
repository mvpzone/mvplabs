# Session Observatory — Modular SQL Queries

Individual `.sql` files for loading into BQ Studio. Each file is a single query (or small set) with header comments explaining the scenario, what to look for, and expected results.

## Lab 1: Forensic Ledger Investigation (Day 1 PM)

**Scenario**: "Agent spent $4,200 at 3am. CISO wants proof."

| # | File | Query | Table |
|---|------|-------|-------|
| 1 | `lab1_01_session_inventory.sql` | Find session by user + time range | `session_ledger` |
| 2 | `lab1_02_event_timeline.sql` | Trace full event sequence + delegation chain | `session_events_log` |
| 3 | `lab1_03_mandate_verification.sql` | Verify mandate authorization + constraints | `mandate_ledger` |
| 4 | `lab1_04_attestation_coverage.sql` | Check L1/L2/L3 attestation integrity | `session_events_log` |
| 5 | `lab1_05_execution_compliance.sql` | Verify per-execution compliance | `mandate_executions_log` |
| 6 | `lab1_06_deep_inspection.sql` | Extract attestation evidence for independent verify | `session_events_log` |

## Lab 2: Behavioral Forensics (Day 2 PM)

| # | File | Query | Table |
|---|------|-------|-------|
| 1 | `lab2_01_session_overview.sql` | All sessions in last 24h with trust scores | `session_ledger` |
| 2 | `lab2_02_behavioral_anomaly.sql` | Flagged events + high token consumption | `session_events_log` |
| 3 | `lab2_03_attestation_integrity.sql` | L1/L2/L3 status across all events | `session_events_log` |
| 4 | `lab2_04_token_timeline.sql` | Token volume over time (detect spikes) | `session_events_log` |

## How to Use in BQ Studio

1. Open [BQ Console](https://console.cloud.google.com/bigquery)
2. Select the correct project (npprd or pprd)
3. Click **+ Compose new query**
4. Paste the contents of the `.sql` file
5. Replace `@parameter` placeholders with actual values
6. Run

## Related

- **Full monolith**: `../session_observatory.sql` (all session domain queries)
- **Notebook**: `../../nb/session_observatory.ipynb` (session + mandate domains)
- **Query catalog**: `../../../../pyful-agents/docs/design/QUERY_CATALOG.md` (95+ query inventory)
- **Canonical doc**: [III-14 Session Observatory](../../../../../nodecloud/nodeful-docs/tspace/zero-trust/III-14-session-observatory.md)

## BQ Dataset

- **Dataset**: `pyagents`
- **Tables**: `session_events_log`, `session_ledger`, `mandate_ledger`, `mandate_executions_log`
- **Access**: Participants need `bigquery.dataViewer` role on the `pyagents` dataset
