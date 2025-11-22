# Great Expectations Data Quality Layer

This directory implements formal data quality validation using [Great Expectations](https://greatexpectations.io/) to ensure semantic consistency before embedding refresh and downstream AI tasks.

## Why It's Here (Interview Context)
Demonstrates production-grade data quality practices for Analytics/Data Engineer roles:
- **Semantic contracts:** Enforce domain values, text length bounds, schema stability.
- **Shift-left testing:** Catch data drift before embeddings/RAG propagate errors.
- **Governance:** Version-controlled expectations show quality standards.
- **SLA enforcement:** Pipeline fails fast on quality violations (no stale vector representations).

## Structure
```
great_expectations/
├── great_expectations.yml        # Config (DuckDB datasource, stores)
├── expectations/
│   └── document_index_suite.json # Validation rules for document_index mart
├── checkpoints/
│   └── document_index_checkpoint.yml  # Checkpoint to run suite
├── uncommitted/                  # Runtime artifacts (validations, data docs)
└── plugins/                      # Custom expectations (if needed)
```

## Expectation Suite: `document_index_suite`
Located at `expectations/document_index_suite.json`

**Validations:**
1. **Row count:** 15-50 documents (reasonable corpus size).
2. **Schema:** Exact columns `[doc_id, domain, text, source_table]` in order.
3. **doc_id:** Not null, unique (primary key contract).
4. **domain:** Not null, must be in `["hr", "legal", "technical"]` (prevents semantic drift).
5. **text:** Not null, length 50-20000 chars (embedding input bounds).
6. **source_table:** Not null, must be in `["hr_policy", "arbitration_subrogation", "ml_concepts"]` (lineage).

## Checkpoint: `document_index_checkpoint`
Located at `checkpoints/document_index_checkpoint.yml`

Runs the `document_index_suite` against `main_marts.document_index` in DuckDB warehouse.

**Actions:**
- Stores validation results in `uncommitted/validations/`.
- Updates HTML Data Docs in `uncommitted/data_docs/`.

## Running Locally

### Prerequisites
```bash
pip install great-expectations==0.18.12
```

### Execute Checkpoint
```bash
cd great_expectations
REPO_ROOT=$(pwd)/.. great_expectations checkpoint run document_index_checkpoint
```

If validation passes, exit code 0. If any expectation fails, exit code non-zero + detailed results in `uncommitted/validations/`.

### View Data Docs (HTML Report)
```bash
great_expectations docs build
# Opens browser with validation results, profiling, and expectation details
```

## Integration with Airflow
The DAG task `ge_document_index_validation` runs the checkpoint:
```python
ge_validate = BashOperator(
    task_id="ge_document_index_validation",
    bash_command="cd $REPO_ROOT && REPO_ROOT=$(pwd) great_expectations checkpoint run document_index_checkpoint"
)
```
**Pipeline flow:** `dbt_test` → `ge_validate` → `refresh_embeddings`

If GE fails, the pipeline stops—preventing corrupted embeddings from being built.

## Example Failure Scenario
**Scenario:** A new document is ingested with domain "finance" (not in allowed set).

**Result:**
- GE checkpoint fails on `expect_column_values_to_be_in_set`.
- Airflow marks `ge_document_index_validation` task as failed.
- Downstream `refresh_embeddings` does not run.
- Alert/notification can be added (e.g., Slack via Airflow action).

**Resolution:**
1. Investigate source data (staging table or seed).
2. Either fix the domain value OR update expectation suite to include "finance" (version-controlled change).
3. Rerun pipeline after fix.

## Comparison: dbt Tests vs Great Expectations
| Aspect | dbt Tests | Great Expectations |
|--------|-----------|-------------------|
| Schema | ✅ not_null, unique, relationships | ✅ + column order, type inference |
| Values | ✅ accepted_values | ✅ + in_set, regex, ranges |
| Distribution | ❌ Limited | ✅ mean, std, quantiles |
| Row count | ❌ Custom test needed | ✅ Native `expect_table_row_count_to_be_between` |
| Reporting | Terminal + logs | ✅ Rich HTML Data Docs |

**Strategy:** Use both—dbt for structural tests, GE for semantic + statistical validation.

## Common Expectations You Can Add
- `expect_column_mean_to_be_between` (e.g., average text length stability)
- `expect_column_quantile_values_to_be_between` (distribution checks)
- `expect_column_values_to_match_regex` (e.g., doc_id format `^[a-f0-9\-]{36}$` for UUIDs)
- `expect_column_pair_values_a_to_be_greater_than_b` (cross-column logic)
- Custom Python expectations for domain-specific rules

## CI/CD Integration
The GitHub Actions workflow (`.github/workflows/airflow-ci.yml`) runs the GE checkpoint:
```yaml
airflow tasks test data_platform_pipeline ge_document_index_validation "$EXEC_DATE"
```
Artifacts uploaded: validation results JSON + rendered DAG graph.

## Interview Talking Points
- "I added GE to enforce semantic contracts—domain drift is detected before embedding refresh, reducing hallucination risk."
- "The checkpoint gates downstream tasks; if validation fails, we don't pollute the vector store."
- "Data Docs provide stakeholders visibility into quality metrics without reading code."
- "This pattern mirrors production practices at companies with formal data SLAs."

## Extending
Ideas:
- Add suite for `hr_policy_features` (validate flag counts, value distributions).
- Add suite for `arbitration_timelines` (ensure deadline dates are future, no nulls).
- Implement statistical expectations (z-score anomaly detection on row counts).
- Add Slack notification action on validation failure.
- Schedule daily Data Docs publish to static site (GitHub Pages).

## Troubleshooting
**Issue:** `No module named 'great_expectations'`
- **Fix:** Install via `pip install great-expectations==0.18.12` OR ensure `airflow/requirements-airflow.txt` includes it.

**Issue:** Checkpoint fails with "datasource not found"
- **Fix:** Ensure `REPO_ROOT` env var is set. The config uses `${REPO_ROOT}` substitution for DuckDB path.

**Issue:** Validation results not persisted
- **Fix:** Check `uncommitted/validations/` exists and is writable. GE creates it automatically on first run.

## Resources
- [Great Expectations Docs](https://docs.greatexpectations.io/)
- [Expectation Gallery](https://greatexpectations.io/expectations/) (browse ~300+ built-in expectations)
- [dbt + GE Integration Patterns](https://docs.greatexpectations.io/docs/deployment_patterns/dbt)

## Next Steps
1. Run checkpoint locally to see HTML report: `great_expectations docs build`.
2. Introduce a deliberate failure (e.g., add a seed row with domain "unknown") and watch pipeline halt.
3. Add statistical expectations (mean text length) for richer monitoring.
4. Wire Slack alerts on failure via Airflow or GE actions.

---
Built to showcase production data quality practices using 100% open-source tools.
