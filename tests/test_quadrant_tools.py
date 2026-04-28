"""Unit tests for the three quadrant CLI utilities under
`agent_configs/quadrant/tools/`. Tests cover the pure-logic functions only
(no network, no PDFs); the CLI wrappers are kept thin so this is sufficient.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = REPO_ROOT / "agent_configs" / "quadrant" / "tools"
sys.path.insert(0, str(TOOLS_DIR))


# ---- pdf2sections --------------------------------------------------------

def test_pdf2sections_basic_split():
    from pdf2sections import split_sections

    text = (
        "Abstract\n"
        "this paper is about X\n"
        "\n"
        "1 Introduction\n"
        "the intro is here\n"
        "\n"
        "2 Related Work\n"
        "prior work\n"
        "\n"
        "References\n"
        "bib1\n"
        "bib2\n"
    )
    sections = split_sections(text)
    assert "abstract" in sections
    assert "introduction" in sections
    assert "related_work" in sections
    assert "references" in sections
    assert "this paper is about X" in sections["abstract"]
    assert "the intro is here" in sections["introduction"]
    assert "prior work" in sections["related_work"]
    assert "bib1" in sections["references"]


def test_pdf2sections_preserves_order():
    from pdf2sections import split_sections

    text = "Abstract\nA\nIntroduction\nB\nMethods\nC\n"
    sections = split_sections(text)
    keys = list(sections.keys())
    assert keys.index("abstract") < keys.index("introduction") < keys.index("methods")


def test_pdf2sections_handles_numbered_and_dotted():
    from pdf2sections import split_sections

    text = "1. Introduction\nfoo\n2. Methods\nbar\n3 Experiments\nbaz\n"
    sections = split_sections(text)
    assert "introduction" in sections
    assert "methods" in sections
    assert "experiments" in sections


def test_pdf2sections_ignores_inline_keyword():
    from pdf2sections import split_sections

    # "method" appears inline but not as a heading; should not split.
    text = "Abstract\nWe present a method for X\nIntroduction\nfoo\n"
    sections = split_sections(text)
    assert "We present a method for X" in sections["abstract"]
    assert "method" not in sections or sections.get("method", "") == ""


def test_pdf2sections_empty_input():
    from pdf2sections import split_sections

    assert split_sections("") == {}


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
