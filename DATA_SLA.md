# Data Pipeline SLAs & Quality Standards

This document codifies expected service levels for the analytics & AI data platform layers.

## Scope
Applies to the daily pipeline (dbt seed/run/test + semantic checks + embeddings refresh + vector verification) executed via GitHub Actions and optionally Airflow.

## Schedule & Freshness
| Layer | Expected Completion (UTC) | Grace Period | Artifact |
|-------|---------------------------|--------------|----------|
| dbt transformations (marts) | 05:00 | 30 min | `document_index` view, derived marts |
| Structural tests (dbt) | 05:05 | 15 min | dbt test results (all green) |
| Semantic validation (GE + manual) | 05:10 | 15 min | GE checkpoint & semantic script logs |
| Embedding refresh | 05:15 | 30 min | Chroma persistent store |
| Metrics snapshot (future daily job) | 05:20 | 30 min | Row counts + drift stats |

## Quality Gates
1. dbt Tests: All not_null, relationships, accepted_values must pass.
2. Great Expectations Suite: All expectations in `document_index_suite` must pass.
3. Semantic Checks: Row count stability, domain enumeration, text length bounds.
4. Drift / Anomaly (future): Embedding norm drift < threshold; row count Z-score < 3.

## Alerting
| Condition | Channel | Severity | Action |
|-----------|---------|----------|--------|
| Structural test failure | Slack webhook | warning | Investigate schema change; rerun pipeline |
| Semantic / GE failure | Slack webhook | error | Block embeddings; fix source or expectations |
| Embedding refresh latency breach | Slack webhook | warning | Profile performance; optimize embedding batch size |
| Drift flag TRUE | Slack webhook | error | Pause downstream RAG usage; analyze drift cause |
| Anomaly Z-score >= 3 | Slack webhook | warning | Validate new ingestion or rollback |

## Escalation Timeline
- T+0 min: Failure detected, Slack alert fired.
- T+15 min: Owner triages logs & identifies scope (structural vs source issue).
- T+30 min: Decision to hotfix expectations, revert data change, or re-run pipeline.
- T+60 min: If unresolved, escalate to data platform lead and annotate `INCIDENTS.md` (future file).

## Recovery Procedures
| Failure Type | Recovery Steps |
|--------------|----------------|
| dbt test regression | Inspect failing test → revert last commit or adjust seed data → rerun `dbt test` |
| GE expectation mismatch | Compare actual values vs expectation config → update suite if legit change → re-run checkpoint |
| Semantic row count spike | Verify new source additions; if unplanned, revert seed / transformation commit |
| Embedding drift | Recompute embeddings; inspect model version & input distribution; validate baseline file |
| Vector store mismatch | Re-run refresh with `--reset`; confirm document_index row counts |

## Ownership
| Domain | Primary Owner | Backup |
|--------|---------------|--------|
| HR policy data | HR Data Steward (simulated) | Data Platform |
| Arbitration/Subrogation | Legal Data Steward (simulated) | Data Platform |
| ML concepts | AI Enablement (simulated) | Data Platform |
| Pipeline orchestration | Data Platform | DevOps (simulated) |
| Embeddings & RAG layer | Data Platform | AI Enablement |

## SLA Violations Tracking
Planned future file: `INCIDENTS.md` recording timestamp, metric impacted, root cause, remediation, and prevention follow-up action.

## Change Control
- Any modification to SLAs requires PR labeled `data-sla` and update to metrics table in `METRICS.md` if related.
- Add new gates only after baseline data collected for >7 days to avoid premature false positives.

## Non-Goals (Out of Scope Initially)
- Real-time streaming freshness guarantees.
- PII detection & masking workflow.
- Automated rollback of embedding store.

## Future Enhancements
- Add freshness lag metric once ingestion timestamps are available.
- Implement automated baseline recomputation for drift thresholds (monthly).
- Introduce anomaly severity tiers (info/warn/error) with dynamic thresholds.
