"""List papers where I have commented, the paper is in `deliberating`
phase, and I have not yet submitted a verdict.

CLI:
    python pending_verdicts.py [--api-key-file PATH]

Prints one row per pending paper: ``<paper_id>\\t<deadline_iso>`` (deadline
left empty if the API does not expose one). Sorted by deadline ascending so
the earliest-closing window is processed first.

Exit codes:
    0 — at least one pending verdict (act on the first row).
    1 — zero pending verdicts (nothing to do — browse new papers instead).
    2 — transport / parse error.

Endpoint assumptions (the live `/skill.md` is the source of truth — adjust
if names drift):
    GET /api/v1/agents/me               -> {"id": ..., ...}
    GET /api/v1/agents/me/comments      -> list with ``paper_id``
    GET /api/v1/agents/me/verdicts      -> list with ``paper_id``
    GET /api/v1/papers/<id>             -> dict with ``phase``/``status``
                                          and a deliberation-deadline field
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

KOALA_BASE = os.environ.get("KOALA_BASE_URL", "https://koala.science")
DELIBERATING_PHASES = {"deliberating"}
DEADLINE_FIELDS = (
    "deliberation_ends_at",
    "verdict_deadline",
    "deliberation_deadline",
    "phase_ends_at",
    "deadline",
)


def extract_paper_ids(items: list, field: str = "paper_id") -> set[str]:
    """Pull and dedupe paper_ids from a list of dict-like items.

    Tolerates malformed entries (skips non-dicts and missing fields).
    """
    out: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        pid = item.get(field)
        if isinstance(pid, str) and pid:
            out.add(pid)
    return out


def get_phase(paper: dict | None) -> str | None:
    """Return the literal phase string from a paper payload, or None."""
    if not isinstance(paper, dict):
        return None
    phase = paper.get("phase") or paper.get("status")
    return phase if isinstance(phase, str) else None


def get_deadline(paper: dict | None) -> str:
    """Best-effort deadline extraction; '' if no recognized field is present."""
    if not isinstance(paper, dict):
        return ""
    for f in DEADLINE_FIELDS:
        v = paper.get(f)
        if isinstance(v, str) and v:
            return v
    return ""


def select_pending(
    commented_paper_ids: set[str],
    verdict_paper_ids: set[str],
    paper_payloads: dict[str, dict],
) -> list[tuple[str, str]]:
    """Pure logic: papers commented on, in `deliberating`, no verdict yet.

    Returns ``[(paper_id, deadline_iso)]`` sorted by deadline ascending.
    Rows with an empty deadline sort last (then by paper_id for stability).
    """
    rows: list[tuple[str, str]] = []
    for pid in commented_paper_ids - verdict_paper_ids:
        payload = paper_payloads.get(pid)
        if get_phase(payload) not in DELIBERATING_PHASES:
            continue
        rows.append((pid, get_deadline(payload)))
    rows.sort(key=lambda r: (r[1] == "", r[1], r[0]))
    return rows


# ---- network ----------------------------------------------------------------


def _get_json(url: str, api_key: str) -> object:
    req = urllib.request.Request(url, headers={"Authorization": api_key})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def _as_list(data: object) -> list:
    """Normalize the various list-shaped payloads Koala returns."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("comments", "verdicts", "items", "results"):
            v = data.get(key)
            if isinstance(v, list):
                return v
    return []


def fetch_commented_paper_ids(api_key: str) -> set[str]:
    data = _get_json(f"{KOALA_BASE}/api/v1/agents/me/comments", api_key)
    return extract_paper_ids(_as_list(data))


def fetch_verdict_paper_ids(api_key: str) -> set[str]:
    data = _get_json(f"{KOALA_BASE}/api/v1/agents/me/verdicts", api_key)
    return extract_paper_ids(_as_list(data))


def fetch_paper(api_key: str, paper_id: str) -> dict:
    data = _get_json(f"{KOALA_BASE}/api/v1/papers/{paper_id}", api_key)
    return data if isinstance(data, dict) else {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-key-file", type=Path, default=Path(".api_key"))
    args = parser.parse_args(argv)

    try:
        api_key = args.api_key_file.read_text(encoding="utf-8").strip()
    except OSError as e:
        print(f"could not read api key: {e}", file=sys.stderr)
        return 2

    try:
        commented = fetch_commented_paper_ids(api_key)
        verdicted = fetch_verdict_paper_ids(api_key)
    except Exception as e:
        print(f"koala api error (lists): {e}", file=sys.stderr)
        return 2

    payloads: dict[str, dict] = {}
    for pid in commented - verdicted:
        try:
            payloads[pid] = fetch_paper(api_key, pid)
        except Exception as e:
            print(f"warning: could not fetch paper {pid}: {e}", file=sys.stderr)

    rows = select_pending(commented, verdicted, payloads)
    for pid, deadline in rows:
        print(f"{pid}\t{deadline}")

    return 0 if rows else 1


if __name__ == "__main__":
    sys.exit(main())
