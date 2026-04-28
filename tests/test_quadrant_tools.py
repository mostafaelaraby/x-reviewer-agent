"""Unit tests for the three quadrant CLI utilities under
`agent_configs/quadrant/tools/`. Tests cover the pure-logic functions only
(no network, no PDFs); the CLI wrappers are kept thin so this is sufficient.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = REPO_ROOT / "agent_configs" / "quadrant" / "tools"
sys.path.insert(0, str(TOOLS_DIR))


# ---- karma_check ---------------------------------------------------------

def test_karma_check_above_floor():
    from karma_check import is_above_floor

    assert is_above_floor({"karma": 99.0}, 10.0) is True


def test_karma_check_at_floor_is_above():
    from karma_check import is_above_floor

    assert is_above_floor({"karma": 10.0}, 10.0) is True


def test_karma_check_below_floor():
    from karma_check import is_above_floor

    assert is_above_floor({"karma": 5.0}, 10.0) is False


def test_karma_check_missing_field():
    from karma_check import is_above_floor

    # Defensive: missing field treated as 0.0 (boundary parse).
    assert is_above_floor({}, 10.0) is False


# ---- already_reviewed ----------------------------------------------------

def test_already_reviewed_finds_self():
    from already_reviewed import has_my_comment

    comments = [
        {"author_id": "other-id", "id": "c1"},
        {"author_id": "my-id", "id": "c2"},
    ]
    assert has_my_comment(comments, "my-id") is True


def test_already_reviewed_not_found():
    from already_reviewed import has_my_comment

    comments = [{"author_id": "other-id", "id": "c1"}]
    assert has_my_comment(comments, "my-id") is False


def test_already_reviewed_empty():
    from already_reviewed import has_my_comment

    assert has_my_comment([], "my-id") is False


def test_already_reviewed_alternate_author_field():
    """Some endpoints use `agent_id` instead of `author_id`."""
    from already_reviewed import has_my_comment

    comments = [{"agent_id": "my-id", "id": "c1"}]
    assert has_my_comment(comments, "my-id") is True


# ---- pending_verdicts ----------------------------------------------------


def test_extract_paper_ids_basic():
    from pending_verdicts import extract_paper_ids

    items = [
        {"paper_id": "p1", "id": "c1"},
        {"paper_id": "p2", "id": "c2"},
        {"paper_id": "p1", "id": "c3"},  # duplicate
    ]
    assert extract_paper_ids(items) == {"p1", "p2"}


def test_extract_paper_ids_skips_malformed():
    from pending_verdicts import extract_paper_ids

    items = [
        "not a dict",
        {"paper_id": None},
        {"paper_id": ""},
        {"id": "c1"},  # missing paper_id
        {"paper_id": "p1"},
    ]
    assert extract_paper_ids(items) == {"p1"}


def test_extract_paper_ids_empty():
    from pending_verdicts import extract_paper_ids

    assert extract_paper_ids([]) == set()


def test_get_phase_prefers_phase_over_status():
    from pending_verdicts import get_phase

    assert get_phase({"phase": "deliberating", "status": "in_review"}) == "deliberating"


def test_get_phase_falls_back_to_status():
    from pending_verdicts import get_phase

    assert get_phase({"status": "deliberating"}) == "deliberating"


def test_get_phase_returns_none_when_missing():
    from pending_verdicts import get_phase

    assert get_phase({}) is None
    assert get_phase(None) is None


def test_get_deadline_picks_first_recognized_field():
    from pending_verdicts import get_deadline

    assert get_deadline({"deliberation_ends_at": "2026-04-30T00:00:00Z"}) == "2026-04-30T00:00:00Z"
    assert get_deadline({"verdict_deadline": "2026-04-30T01:00:00Z"}) == "2026-04-30T01:00:00Z"


def test_get_deadline_empty_when_no_field():
    from pending_verdicts import get_deadline

    assert get_deadline({}) == ""
    assert get_deadline(None) == ""


def test_select_pending_returns_only_deliberating_without_verdict():
    from pending_verdicts import select_pending

    commented = {"p_delib", "p_review", "p_done", "p_verdicted"}
    verdicted = {"p_verdicted"}
    payloads = {
        "p_delib": {"phase": "deliberating", "deliberation_ends_at": "2026-04-29T12:00:00Z"},
        "p_review": {"phase": "in_review"},
        "p_done": {"phase": "reviewed"},
        "p_verdicted": {"phase": "deliberating"},
    }
    rows = select_pending(commented, verdicted, payloads)
    assert rows == [("p_delib", "2026-04-29T12:00:00Z")]


def test_select_pending_sorts_by_deadline_then_id():
    from pending_verdicts import select_pending

    commented = {"a", "b", "c"}
    payloads = {
        "a": {"phase": "deliberating", "deliberation_ends_at": "2026-04-30T00:00:00Z"},
        "b": {"phase": "deliberating", "deliberation_ends_at": "2026-04-29T00:00:00Z"},
        "c": {"phase": "deliberating"},  # no deadline -> sorts last
    }
    rows = select_pending(commented, set(), payloads)
    assert [r[0] for r in rows] == ["b", "a", "c"]


def test_select_pending_empty_inputs():
    from pending_verdicts import select_pending

    assert select_pending(set(), set(), {}) == []


def test_select_pending_skips_paper_with_missing_payload():
    from pending_verdicts import select_pending

    commented = {"p1"}
    rows = select_pending(commented, set(), {})  # no payload entry
    assert rows == []
