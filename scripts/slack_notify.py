#!/usr/bin/env python3
"""Send a Slack notification via incoming webhook.
Usage:
  python scripts/slack_notify.py "Message text" [status]
Environment:
  SLACK_WEBHOOK_URL must be set.
Status (optional): success|failure|warning determines emoji prefix.
"""
import os, sys, json, urllib.request

webhook = os.getenv("SLACK_WEBHOOK_URL")
if not webhook:
    print("No SLACK_WEBHOOK_URL provided; skipping Slack notification.")
    sys.exit(0)

if len(sys.argv) < 2:
    print("Usage: slack_notify.py <message> [status]")
    sys.exit(1)

message = sys.argv[1]
status = sys.argv[2] if len(sys.argv) > 2 else "info"
emoji_map = {
    "success": ":white_check_mark:",
    "failure": ":rotating_light:",
    "warning": ":warning:",
    "info": ":information_source:"}
emoji = emoji_map.get(status, ":information_source:")
text = f"{emoji} {message}"

payload = {"text": text}
req = urllib.request.Request(webhook, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req) as resp:
        print(f"Slack response: {resp.status}")
except Exception as e:
    print(f"Slack notification failed: {e}")
    sys.exit(0)
