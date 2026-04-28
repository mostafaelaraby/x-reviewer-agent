"""Check the agent's current Koala karma balance.

CLI:
    python karma_check.py [--floor N] [--quiet]

  Reads `.api_key` from cwd (override with --api-key-file), fetches
  `/api/v1/agents/me`, prints the karma balance, and exits:
    0 if karma >= floor
    1 if karma < floor (orchestrator should pivot to verdict-only mode)
    2 on transport / parse error.

  Default floor: 10.0 (≈10 first-comments of headroom).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

KOALA_BASE = os.environ.get("KOALA_BASE_URL", "https://koala.science")


def is_above_floor(profile: dict, floor: float) -> bool:
    """True if profile's karma is at or above the floor.

    Missing field is treated as 0.0 (system-boundary parsing).
    """
    karma = profile.get("karma")
    if karma is None:
        return False
    try:
        return float(karma) >= float(floor)
    except (TypeError, ValueError):
        return False


def fetch_profile(api_key: str) -> dict:
    req = urllib.request.Request(
        f"{KOALA_BASE}/api/v1/agents/me",
        headers={"Authorization": api_key},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--floor", type=float, default=10.0,
                        help="Karma floor (default: 10.0).")
    parser.add_argument("--quiet", action="store_true",
                        help="Do not print the karma value.")
    parser.add_argument("--api-key-file", type=Path, default=Path(".api_key"),
                        help="Path to .api_key file (default: ./.api_key).")
    args = parser.parse_args(argv)

    try:
        api_key = args.api_key_file.read_text(encoding="utf-8").strip()
    except OSError as e:
        print(f"could not read api key: {e}", file=sys.stderr)
        return 2

    try:
        profile = fetch_profile(api_key)
    except Exception as e:
        print(f"could not fetch /agents/me: {e}", file=sys.stderr)
        return 2

    karma = profile.get("karma", 0.0)
    if not args.quiet:
        print(f"{karma}")

    return 0 if is_above_floor(profile, args.floor) else 1


if __name__ == "__main__":
    sys.exit(main())
