#!/usr/bin/env python3
"""Embedding drift detection for vector store quality monitoring.

Compares current embedding statistics (L2 norm mean/std) against a historical baseline
to detect distribution shifts that could indicate:
- Model version changes
- Input text quality degradation
- Encoding configuration drift

Exits with non-zero code if drift exceeds threshold, enabling pipeline gating.
"""
import argparse
import json
import os
import sys
from pathlib import Path

import chromadb
import numpy as np


def load_baseline(baseline_path: Path) -> dict:
    """Load historical baseline statistics from JSON file."""
    if not baseline_path.exists():
        return None
    with open(baseline_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_baseline(baseline_path: Path, stats: dict):
    """Save current statistics as new baseline."""
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    with open(baseline_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(f"✅ Saved new baseline to {baseline_path}")


def compute_embedding_stats(persist_dir: Path, collection_name: str) -> dict:
    """Compute L2 norm statistics from Chroma vector store."""
    client = chromadb.PersistentClient(path=str(persist_dir))
    try:
        collection = client.get_collection(name=collection_name)
    except ValueError:
        print(f"❌ Collection '{collection_name}' not found in {persist_dir}")
        sys.exit(1)

    results = collection.get(include=["embeddings"])
    embeddings = results.get("embeddings", [])
    
    if len(embeddings) == 0:
        print(f"⚠️  No embeddings found in collection '{collection_name}'")
        return {"count": 0, "norm_mean": 0.0, "norm_std": 0.0}

    norms = [np.linalg.norm(emb) for emb in embeddings]
    return {
        "count": len(norms),
        "norm_mean": float(np.mean(norms)),
        "norm_std": float(np.std(norms)),
        "norm_min": float(np.min(norms)),
        "norm_max": float(np.max(norms)),
    }


def check_drift(current: dict, baseline: dict, threshold: float) -> tuple[bool, str]:
    """Check if current stats exceed drift threshold relative to baseline.
    
    Returns:
        (has_drift, reason)
    """
    if baseline is None:
        return False, "No baseline available (first run)"
    
    if current["count"] == 0:
        return True, "No embeddings in current collection"
    
    if baseline["count"] == 0:
        return False, "Baseline had no embeddings (initializing)"

    # Calculate relative drift in mean L2 norm
    mean_drift_pct = abs(current["norm_mean"] - baseline["norm_mean"]) / baseline["norm_mean"] * 100
    
    if mean_drift_pct > threshold:
        return True, f"Norm mean drift {mean_drift_pct:.2f}% exceeds threshold {threshold}%"
    
    return False, f"Drift {mean_drift_pct:.2f}% within threshold"


def main():
    parser = argparse.ArgumentParser(description="Detect embedding distribution drift")
    parser.add_argument(
        "--persist-dir",
        type=Path,
        default=Path("project3-document-qa/chroma_store"),
        help="Path to Chroma persistent directory",
    )
    parser.add_argument(
        "--collection",
        default="documents",
        help="Chroma collection name",
    )
    parser.add_argument(
        "--baseline-file",
        type=Path,
        default=Path("metrics/baselines/embedding_norm.json"),
        help="Path to baseline statistics JSON",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=10.0,
        help="Drift threshold as percentage of baseline mean (default: 10%%)",
    )
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Update baseline with current statistics (use after validating drift is expected)",
    )
    parser.add_argument(
        "--failures-file",
        type=Path,
        help="Write failures JSON for Slack --failures-file integration",
    )

    args = parser.parse_args()

    print(f"🔍 Computing embedding statistics from {args.persist_dir}...")
    current_stats = compute_embedding_stats(args.persist_dir, args.collection)
    
    print(f"📊 Current stats:")
    print(f"   Count: {current_stats['count']}")
    print(f"   Norm mean: {current_stats['norm_mean']:.4f}")
    print(f"   Norm std: {current_stats['norm_std']:.4f}")
    print(f"   Norm range: [{current_stats.get('norm_min', 0):.4f}, {current_stats.get('norm_max', 0):.4f}]")

    baseline = load_baseline(args.baseline_file)
    if baseline:
        print(f"📈 Baseline (from {args.baseline_file}):")
        print(f"   Count: {baseline['count']}")
        print(f"   Norm mean: {baseline['norm_mean']:.4f}")
        print(f"   Norm std: {baseline['norm_std']:.4f}")

    has_drift, reason = check_drift(current_stats, baseline, args.threshold)
    
    if args.update_baseline:
        save_baseline(args.baseline_file, current_stats)
        return 0

    if has_drift:
        print(f"🚨 DRIFT DETECTED: {reason}")
        if args.failures_file:
            failures = {
                "failures": [
                    f"Embedding drift detected: {reason}",
                    f"Current norm mean: {current_stats['norm_mean']:.4f}",
                    f"Baseline norm mean: {baseline['norm_mean']:.4f}" if baseline else "No baseline",
                ]
            }
            args.failures_file.parent.mkdir(parents=True, exist_ok=True)
            with open(args.failures_file, "w", encoding="utf-8") as f:
                json.dump(failures, f, indent=2)
            print(f"📝 Wrote failure details to {args.failures_file}")
        return 1
    else:
        print(f"✅ No drift: {reason}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
