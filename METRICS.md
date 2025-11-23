# Canonical Metrics

This document defines the core analytics & reliability metrics produced or governed by the pipeline. Each metric lists: name, grain, purpose, formula/source, refresh cadence, owner, and SLA target.

## Table
| Metric | Grain | Purpose | Source / Formula | Refresh Cadence | Owner | SLA / Target |
|--------|-------|---------|------------------|-----------------|-------|--------------|
| document_index_total_rows | Daily snapshot | Size of unified corpus powering RAG & analytics | `SELECT COUNT(*) FROM document_index` | Daily (05:00 UTC) | Data Platform | > 20 rows (non-zero); change delta < 50% unless planned |
| hr_policy_count | Daily snapshot | Track HR policy document coverage | `SELECT COUNT(*) FROM stg_hr_policy` | Daily | HR Data Steward | Stable +/- 10% week-over-week |
| arbitration_case_count | Daily snapshot | Volume of arbitration/subrogation documents | `SELECT COUNT(*) FROM stg_arbitration_subrogation` | Daily | Legal Data Steward | Stable +/- 25% week-over-week |
| ml_concept_count | Daily snapshot | Coverage of ML concept glossary | `SELECT COUNT(*) FROM stg_ml_concepts` | Daily | AI Enablement | Minimum 10 concepts; grow over time |
| avg_policy_text_length | Daily snapshot | Content size health / detect truncation | `SELECT AVG(LENGTH(raw_text)) FROM stg_hr_policy` | Daily | Data Platform | > 200 chars; no drop > 30% day-over-day |
| embedding_refresh_latency_seconds | Per run | Operational latency of embedding build step | Measured wall-clock in `refresh_embeddings.py` | Each pipeline run | Data Platform | < 120s local / < 300s CI |
| vector_store_document_count | Daily snapshot | Embedding index completeness | Chroma collection count | Daily | Data Platform | Equals `document_index_total_rows` |
| vector_store_sync_gap | Daily snapshot | Detect sync drift between mart and embeddings | `document_index_total_rows - vector_store_document_count` | Daily | Data Platform | = 0 |
| quality_gate_pass_rate | Weekly aggregate | Reliability of semantic + structural validations | (# successful runs / total runs) | Weekly | Data Platform | > 95% |
| row_count_anomaly_zscore | Daily snapshot (if triggered) | Early volume anomaly detection | Z-score vs 7-day rolling mean | Daily | Data Platform | |Z| < 3 |
| embedding_norm_mean | Daily snapshot | Distribution monitoring for embedding drift | Mean L2 norm across vectors | Daily | Data Platform | Within +/-10% of 30-day baseline |
| embedding_drift_flag | Per run | Binary indicator of drift check breach | Computed in drift script | Each pipeline run | Data Platform | FALSE |

## Metric Notes
- Row-based metrics stored in DuckDB allow lightweight historical snapshots (future enhancement: persist daily snapshot table).
- Drift metrics will be added once `scripts/check_embedding_drift.py` exists; baseline file will live under `metrics/baselines/embedding_norm.json` (to be created in Phase 3).
- Anomaly detection uses a simple Z-score; production systems might adopt robust statistics (median absolute deviation) or seasonality modeling.
- Owners reflect functional accountability (simulated in this portfolio). In an org setting these map to specific teams or individuals.

## Change Management
- Additions / modifications require PR review + update to `DATA_SLA.md` where relevant.
- Decommissioned metrics must include migration note (what replaces it and why).

## Future Extensions
- Introduce dbt exposures for `document_index_total_rows` and `vector_store_document_count` so BI tools can discover lineage automatically.
- Persist daily snapshots in a `metrics_daily` incremental model for trend visualization.
- Add freshness lag metric once external ingestion timestamps exist.
