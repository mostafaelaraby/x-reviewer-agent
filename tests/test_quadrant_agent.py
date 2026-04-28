"""Structural tests for the `quadrant` agent config.

These tests verify that `agent_configs/quadrant/` is populated according to
`.claude/specs/quadrant-agent.md`: a hand-authored main system prompt plus four
claude-code sub-agent definitions under `.claude/agents/`.

All checks are filesystem + pure-Python (no mocks). Tests run from repo root and
locate the agent config via `pathlib.Path(__file__).resolve().parents[1]`.
"""
import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
QUADRANT_DIR = REPO_ROOT / "agent_configs" / "quadrant"
SUBAGENTS_DIR = QUADRANT_DIR / ".claude" / "agents"
SUBAGENT_NAMES = ("citations", "novelty", "rigor", "literature")
PROFILE_DESCRIPTION = (
    "Evaluation role: Senior reviewer, multi-lens (citations, novelty, rigor, literature). "
    "Persona: Skeptical-empirical, formal-academic tone. "
    "Research interests: NLP, LLM alignment, ML evaluation methodology."
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


def test_quadrant_system_prompt_names_all_four_subagents():
    body = _read_system_prompt()
    for sub in SUBAGENT_NAMES:
        assert sub in body, f"sub-agent name {sub!r} missing from system_prompt.md"


def test_quadrant_system_prompt_states_profile_description():
    body = _read_system_prompt()
    assert PROFILE_DESCRIPTION in body, (
        "system_prompt.md must contain the exact profile-description sentence "
        "from Requirement 1"
    )


def test_quadrant_system_prompt_does_not_duplicate_global_rules():
    body = _read_system_prompt().lower()
    forbidden_karma = ("1.0 karma", "0.1 karma")
    forbidden_bands = ("weak accept", "strong accept")
    for token in forbidden_karma + forbidden_bands:
        assert token not in body, (
            f"system_prompt.md must not restate {token!r} "
            "— it lives in GLOBAL_RULES.md"
        )


def test_quadrant_subagents_present():
    assert SUBAGENTS_DIR.is_dir(), (
        f"{SUBAGENTS_DIR} must exist (claude-code sub-agent directory)"
    )
    for name in SUBAGENT_NAMES:
        path = SUBAGENTS_DIR / f"{name}.md"
        assert path.is_file(), f"missing sub-agent file: {path}"


def test_quadrant_subagent_frontmatter_valid():
    for name in SUBAGENT_NAMES:
        path = SUBAGENTS_DIR / f"{name}.md"
        body = path.read_text(encoding="utf-8")
        assert body.startswith("---\n"), f"{path} must start with '---' frontmatter"
        rest = body[4:]
        end = rest.find("\n---\n")
        assert end != -1, f"{path} missing closing '---' frontmatter delimiter"
        front = rest[:end]
        meta = yaml.safe_load(front)
        assert isinstance(meta, dict), f"{path} frontmatter must parse as a YAML mapping"
        assert "name" in meta, f"{path} frontmatter missing 'name'"
        assert "description" in meta, f"{path} frontmatter missing 'description'"
        assert meta["name"] == name, (
            f"{path} frontmatter 'name' ({meta['name']!r}) must equal filename stem ({name!r})"
        )
        assert isinstance(meta["description"], str) and meta["description"].strip(), (
            f"{path} frontmatter 'description' must be a non-empty string"
        )
        sub_body = rest[end + len("\n---\n") :]
        assert sub_body.strip(), f"{path} body (after frontmatter) must be non-empty"


def test_quadrant_system_prompt_has_selectivity_section():
    body = _read_system_prompt()
    assert "## Selectivity" in body, "system_prompt.md must contain '## Selectivity' heading"
    for domain in ("NLP", "LLM alignment", "ML evaluation methodology"):
        assert domain in body, f"selectivity domain {domain!r} missing"


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
