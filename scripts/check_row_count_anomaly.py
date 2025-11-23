#!/usr/bin/env python3
"""Row count anomaly detection for data marts.

Compares current mart row counts against a rolling baseline (7-day window)
using Z-score to detect unexpected volume changes that could indicate:
- Missing or duplicate source data
- Pipeline execution errors
- Unplanned data ingestion

Exits with non-zero code if anomaly detected, enabling pipeline gating.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import duckdb


def load_baseline(baseline_path: Path) -> dict:
    """Load historical row count snapshots from JSON file."""
    if not baseline_path.exists():
        return {"snapshots": []}
    with open(baseline_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_baseline(baseline_path: Path, data: dict):
    """Save updated baseline with new snapshot."""
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    with open(baseline_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_mart_counts(duckdb_path: Path, marts: list[str]) -> dict:
    """Query row counts for specified marts."""
    conn = duckdb.connect(str(duckdb_path), read_only=True)
    counts = {}
    for mart in marts:
        try:
            result = conn.execute(f"SELECT COUNT(*) FROM main_marts.{mart}").fetchone()
            counts[mart] = result[0] if result else 0
        except duckdb.CatalogException:
            print(f"⚠️  Mart '{mart}' not found in database")
            counts[mart] = 0
    conn.close()
    return counts


def compute_zscore(current: int, snapshots: list) -> tuple[float, float, float]:
    """Compute Z-score for current count vs historical mean/std.
    
    Returns:
        (zscore, mean, std)
    """
    if len(snapshots) < 2:
        return 0.0, current, 0.0
    
    historical_counts = [s["count"] for s in snapshots]
    mean = sum(historical_counts) / len(historical_counts)
    variance = sum((x - mean) ** 2 for x in historical_counts) / len(historical_counts)
    std = variance ** 0.5
    
    if std == 0:
        return 0.0, mean, 0.0
    
    zscore = (current - mean) / std
    return zscore, mean, std


def check_anomalies(
    current_counts: dict,
    baseline: dict,
    threshold: float,
    window_size: int
) -> tuple[bool, list[str]]:
    """Check for anomalies in current counts vs baseline.
    
    Returns:
        (has_anomaly, failure_messages)
    """
    failures = []
    
    for mart, current_count in current_counts.items():
        # Filter snapshots for this mart and keep only recent window
        mart_snapshots = [
            s for s in baseline.get("snapshots", [])
            if s.get("mart") == mart
        ][-window_size:]
        
        if len(mart_snapshots) < 2:
            print(f"ℹ️  {mart}: insufficient history ({len(mart_snapshots)} snapshots)")
            continue
        
        zscore, mean, std = compute_zscore(current_count, mart_snapshots)
        
        print(f"📊 {mart}:")
        print(f"   Current: {current_count} rows")
        print(f"   Baseline mean: {mean:.1f} rows (last {len(mart_snapshots)} runs)")
        print(f"   Std dev: {std:.1f}")
        print(f"   Z-score: {zscore:.2f}")
        
        if abs(zscore) >= threshold:
            direction = "spike" if zscore > 0 else "drop"
            failures.append(
                f"{mart}: {direction} detected (Z={zscore:.2f}, current={current_count}, mean={mean:.1f})"
            )
    
    return len(failures) > 0, failures


def main():
    parser = argparse.ArgumentParser(description="Detect row count anomalies in marts")
    parser.add_argument(
        "--duckdb",
        type=Path,
        default=Path("data-platform/dbt/warehouse/data.duckdb"),
        help="Path to DuckDB database",
    )
    parser.add_argument(
        "--marts",
        nargs="+",
        default=["document_index", "hr_policy_features", "arbitration_timelines"],
        help="List of mart names to monitor",
    )
    parser.add_argument(
        "--baseline-file",
        type=Path,
        default=Path("metrics/baselines/row_counts.json"),
        help="Path to baseline row count snapshots JSON",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=3.0,
        help="Z-score threshold for anomaly detection (default: 3.0)",
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=7,
        help="Number of historical snapshots to use for baseline (default: 7)",
    )
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Append current counts to baseline history",
    )
    parser.add_argument(
        "--failures-file",
        type=Path,
        help="Write failures JSON for Slack --failures-file integration",
    )

    args = parser.parse_args()

    print(f"🔍 Querying row counts from {args.duckdb}...")
    current_counts = get_mart_counts(args.duckdb, args.marts)

    baseline = load_baseline(args.baseline_file)
    
    if args.update_baseline:
        timestamp = datetime.utcnow().isoformat()
        for mart, count in current_counts.items():
            baseline.setdefault("snapshots", []).append({
                "timestamp": timestamp,
                "mart": mart,
                "count": count
            })
        save_baseline(args.baseline_file, baseline)
        print(f"✅ Appended {len(current_counts)} snapshots to {args.baseline_file}")
        return 0

    has_anomaly, failures = check_anomalies(
        current_counts,
        baseline,
        args.threshold,
        args.window_size
    )

    if has_anomaly:
        print(f"🚨 ANOMALIES DETECTED:")
        for failure in failures:
            print(f"   • {failure}")
        
        if args.failures_file:
            failures_data = {"failures": failures}
            args.failures_file.parent.mkdir(parents=True, exist_ok=True)
            with open(args.failures_file, "w", encoding="utf-8") as f:
                json.dump(failures_data, f, indent=2)
            print(f"📝 Wrote failure details to {args.failures_file}")
        
        return 1
    else:
        print("✅ No anomalies detected")
        return 0


if __name__ == "__main__":
    sys.exit(main())
