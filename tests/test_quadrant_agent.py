"""Structural tests for the `quadrant` agent config.

The agent is a single-orchestrator design (no sub-agent dispatch) with a
four-lens *checklist* baked into the prompt: citations, novelty, rigor,
literature. These tests verify `agent_configs/quadrant/` is shaped accordingly.

All checks are filesystem + pure-Python (no mocks). Tests run from repo root and
locate the agent config via `pathlib.Path(__file__).resolve().parents[1]`.
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
QUADRANT_DIR = REPO_ROOT / "agent_configs" / "quadrant"
SUBAGENTS_DIR = QUADRANT_DIR / ".claude" / "agents"
LENS_NAMES = ("citations", "novelty", "rigor", "literature")
PROFILE_DESCRIPTION = (
    "Evaluation role: Evidence-calibrated technical reviewer. "
    "Persona: skeptical-empirical, formal-academic, source-grounded. "
    "Research interests: NLP, LLM alignment, computer vision, trustworthy ML, "
    "ML evaluation methodology."
)


def _read_system_prompt() -> str:
    return (QUADRANT_DIR / "system_prompt.md").read_text(encoding="utf-8")


def test_quadrant_dir_exists():
    assert QUADRANT_DIR.is_dir()


def test_quadrant_system_prompt_exists_and_nonempty():
    prompt_path = QUADRANT_DIR / "system_prompt.md"
    assert prompt_path.is_file()
    body = prompt_path.read_text(encoding="utf-8")
    assert body.strip(), "system_prompt.md must be non-empty"
    assert body.lstrip().startswith("# Agent: quadrant"), (
        "system_prompt.md must open with '# Agent: quadrant'"
    )


def test_quadrant_system_prompt_names_all_four_lenses():
    body = _read_system_prompt()
    for lens in LENS_NAMES:
        assert lens in body.lower(), f"lens name {lens!r} missing from system_prompt.md"


def test_quadrant_system_prompt_states_profile_description():
    body = _read_system_prompt()
    assert PROFILE_DESCRIPTION in body, (
        "system_prompt.md must contain the exact senior-reviewer profile description"
    )


def test_quadrant_system_prompt_does_not_duplicate_global_rules():
    """Guard against copy-pasting the full GLOBAL_RULES tables into the prompt.

    Quoting band labels in service of an explicit calibration anchor is fine and
    intentional (see the novelty x rigor rubric in v7). What is *not* fine is
    duplicating the full karma-cost table or the karma starting balance, since
    those live in GLOBAL_RULES.md and drift if restated.
    """
    body = _read_system_prompt().lower()
    forbidden = (
        "first comment or thread on a paper: 1.0",
        "subsequent comment/thread on the same paper: 0.1",
        "starts with 100 karma",
    )
    for token in forbidden:
        assert token not in body, (
            f"system_prompt.md must not restate {token!r} "
            "— it lives in GLOBAL_RULES.md"
        )


def test_quadrant_has_no_subagents():
    """Single-orchestrator design: no `.claude/agents/*.md` files allowed."""
    if not SUBAGENTS_DIR.is_dir():
        return
    leftover = sorted(p.name for p in SUBAGENTS_DIR.glob("*.md"))
    assert not leftover, (
        f"`.claude/agents/` should be empty in the single-orchestrator design; "
        f"found: {leftover}"
    )


def test_quadrant_system_prompt_has_selectivity_section():
    body = _read_system_prompt()
    for domain in ("NLP", "LLM alignment", "ML evaluation methodology"):
        assert domain in body, f"selectivity domain {domain!r} missing"


def test_quadrant_system_prompt_describes_comment_structure():
    body = _read_system_prompt()
    for section in ("Strengths", "Concerns", "Recommendations", "Overall"):
        assert section in body, f"comment-structure section {section!r} missing"


def test_quadrant_compiled_prompt_assembles():
    from reva.prompt import assemble_prompt

    compiled = assemble_prompt(
        global_rules_path=REPO_ROOT / "agent_definition" / "GLOBAL_RULES.md",
        platform_skills_path=REPO_ROOT / "agent_definition" / "platform_skills.md",
        agent_prompt_path=QUADRANT_DIR / "system_prompt.md",
    )
    assert compiled.strip(), "compiled prompt must be non-empty"
    assert "Koala Science platform" in compiled, "GLOBAL_RULES content missing"
    assert "# Agent: quadrant" in compiled, "agent system prompt missing"


def test_quadrant_config_json_uses_claude_code_backend():
    cfg_path = QUADRANT_DIR / "config.json"
    assert cfg_path.is_file()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    assert cfg["backend"] == "claude-code"
