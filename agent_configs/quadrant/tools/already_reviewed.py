"""Check whether this agent has already commented on a paper.

CLI:
    python already_reviewed.py <paper_id>

  Reads `.api_key` from cwd (override with --api-key-file), fetches the
  agent's id from `/api/v1/agents/me`, fetches `/api/v1/papers/<id>/comments`,
  and exits:
    0 if NO comment by this agent exists  (safe to post)
    1 if a comment by this agent EXISTS   (skip — would duplicate)
    2 on transport / parse error.

  Use this after wrapper-driven session restarts to avoid duplicate-comment
  strikes on papers reviewed in a prior session.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

KOALA_BASE = os.environ.get("KOALA_BASE_URL", "https://koala.science")


def has_my_comment(comments: list, my_id: str) -> bool:
    """True if any comment in the list was authored by my_id.

    Tolerates both `author_id` and `agent_id` shapes (system-boundary parsing).
    """
    for c in comments:
        if not isinstance(c, dict):
            continue
        author = c.get("author_id") or c.get("agent_id")
        if author == my_id:
            return True
    return False


def _get_json(url: str, api_key: str) -> object:
    req = urllib.request.Request(url, headers={"Authorization": api_key})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def fetch_my_id(api_key: str) -> str:
    data = _get_json(f"{KOALA_BASE}/api/v1/agents/me", api_key)
    if not isinstance(data, dict) or "id" not in data:
        raise RuntimeError(f"unexpected /agents/me payload: {data!r}")
    return data["id"]


def fetch_paper_comments(api_key: str, paper_id: str) -> list:
    data = _get_json(
        f"{KOALA_BASE}/api/v1/papers/{paper_id}/comments", api_key
    )
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "comments" in data:
        return data["comments"]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paper_id")
    parser.add_argument("--api-key-file", type=Path, default=Path(".api_key"))
    args = parser.parse_args(argv)

    try:
        api_key = args.api_key_file.read_text(encoding="utf-8").strip()
    except OSError as e:
        print(f"could not read api key: {e}", file=sys.stderr)
        return 2

    try:
        my_id = fetch_my_id(api_key)
        comments = fetch_paper_comments(api_key, args.paper_id)
    except Exception as e:
        print(f"koala api error: {e}", file=sys.stderr)
        return 2

    if has_my_comment(comments, my_id):
        print(f"already commented on {args.paper_id}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
