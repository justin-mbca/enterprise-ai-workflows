#!/usr/bin/env python3
"""Send a Slack notification via incoming webhook.

Enhanced usage examples:
  python3 scripts/slack_notify.py "Pipeline succeeded" --level success
  python3 scripts/slack_notify.py "Quality gate failed" --level error --failures-file /path/to/failures.json
  python3 scripts/slack_notify.py "Just a plain message" --no-emoji

Environment:
  SLACK_WEBHOOK_URL must be set (export locally or provided as GitHub Action secret).

Flags:
  --level {success,error,warning,info}  Severity level → maps to emoji.
  --no-emoji                          Disable emoji prefix.
  --failures-file PATH                Append failing expectations or lines from file.
  --raw-json PATH                     Send raw JSON file as payload (overrides other flags except webhook).

If --failures-file is JSON containing a list under key 'failures' OR a top-level list, those items are appended.
Plain text file lines are appended verbatim.

Exit codes:
  0 on success or if webhook missing (non-fatal skip)
  1 on usage error / invalid JSON
  2 on network failure
"""
import os
import sys
import json
import argparse
import urllib.request
import urllib.error


EMOJI_MAP = {
    "success": ":white_check_mark:",
    "failure": ":rotating_light:",  # legacy alias
    "error": ":rotating_light:",
    "warning": ":warning:",
    "info": ":information_source:"
}


def load_failures(path: str):
    if not os.path.exists(path):
        return [f"(failures file not found: {path})"]
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except (OSError, IOError) as e:
        return [f"(unable to read failures file: {e})"]
    if not content:
        return ["(failures file empty)"]
    # Try JSON first
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            if "failures" in data and isinstance(data["failures"], list):
                return [str(item) for item in data["failures"]]
            # Fallback: all stringy values
            return [f"{k}: {v}" for k, v in data.items() if isinstance(v, (str, int, float))]
        if isinstance(data, list):
            return [str(item) for item in data]
    except json.JSONDecodeError:
        # Treat as plain text lines
        return [line for line in content.splitlines() if line.strip()]
    except (ValueError, TypeError) as e:
        return [f"(error parsing failures file: {e})"]
    return ["(unrecognized failures file format)"]


def send_payload(webhook: str, payload: dict):
    req = urllib.request.Request(
        webhook,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        print(f"Slack response: {resp.status}")


def main():
    webhook = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook:
        print("No SLACK_WEBHOOK_URL provided; skipping Slack notification.")
        return 0

    parser = argparse.ArgumentParser(description="Send a Slack notification via incoming webhook.")
    parser.add_argument("message", help="Main message text")
    parser.add_argument("status", nargs="?", help="Deprecated positional status (use --level)")
    parser.add_argument("--level", choices=list(EMOJI_MAP.keys()), default=None, help="Severity level → emoji")
    parser.add_argument("--no-emoji", action="store_true", help="Disable emoji prefix")
    parser.add_argument("--failures-file", help="Append failing expectations from file (JSON or text)")
    parser.add_argument("--raw-json", help="Path to raw JSON payload to send directly")

    args = parser.parse_args()

    if args.raw_json:
        try:
            with open(args.raw_json, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except (OSError, IOError, json.JSONDecodeError) as e:
            print(f"Failed to load raw JSON payload: {e}")
            return 1
        try:
            send_payload(webhook, raw)
            return 0
        except urllib.error.URLError as e:
            print(f"Slack notification failed: {e}")
            return 2

    # Determine level (prefer flag, then positional status)
    level = args.level or (args.status if args.status in EMOJI_MAP else "info")
    emoji = EMOJI_MAP.get(level, EMOJI_MAP["info"]) if not args.no_emoji else ""

    # Basic text assembly
    text_parts = [p for p in [emoji, args.message] if p]

    # Append failures if provided
    if args.failures_file:
        failures = load_failures(args.failures_file)
        if failures:
            # Slack message lines; if too many, truncate
            max_lines = 15
            truncated = failures[:max_lines]
            if len(failures) > max_lines:
                truncated.append(f"(+{len(failures) - max_lines} more omitted)")
            text_parts.append("\n" + "\n".join(f"• {f}" for f in truncated))

    payload = {"text": " ".join(text_parts)}
    try:
        send_payload(webhook, payload)
        return 0
    except urllib.error.URLError as e:
        print(f"Slack notification failed: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
