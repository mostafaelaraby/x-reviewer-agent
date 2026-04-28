# Spec: Quadrant — four-lens reviewing agent

## Goal
Build one Koala-competition reviewing agent named `quadrant` that delegates each paper to four parallel claude-code sub-agents (citations, novelty, rigor, literature), then synthesizes their findings into a single consolidated comment per paper and a calibrated verdict.

## Context

### Relevant files
- `agent_configs/quadrant/` — the agent's working directory at runtime (cwd of the claude-code process). Will be created by `uv run reva create --name quadrant --backend claude-code` *outside* this spec's scope; the spec implementation populates the contents.
- `agent_configs/quadrant/system_prompt.md` — the hand-authored main-agent prompt. Concatenated with `agent_definition/GLOBAL_RULES.md` and `agent_definition/platform_skills.md` by `cli/reva/prompt.py:assemble_prompt` to form the runtime CLAUDE.md.
- `agent_configs/quadrant/.claude/agents/{citations,novelty,rigor,literature}.md` — Claude Code sub-agent definitions. Each is a markdown file with frontmatter (`name`, `description`, optional `tools`) plus a system-prompt body. claude-code automatically discovers `.claude/agents/*.md` from cwd, so no harness changes are needed.
- `agent_definition/GLOBAL_RULES.md` — platform-wide rules (read-only here). Defines karma economics, comment shape, verdict rules, score bands, moderation policy, branch policy for reasoning files. **Do not restate any of this in the agent prompt.**
- `agent_definition/platform_skills.md` — points the agent at `{KOALA_BASE_URL}/skill.md` for live MCP/API docs. The compiled prompt already includes this; the agent prompt should not duplicate.
- `cli/reva/backends.py:44` — confirms claude-code launches with `--mcp-config` for Paper Lantern; the Koala MCP key is provided via `.api_key` environment variable.
- `tests/test_cli.py` — pattern for prompt-assembly and agent-config tests. New tests for quadrant follow the same `pathlib`-based structural-check style.

### Current behavior
No `quadrant` agent exists. `agent_configs/` contains only `example-*` stubs with empty system prompts.

### How this fits
This is one of up to three agents the user may register under their OpenReview ID. It uses one slot. Other slots remain free for future, complementary agents (e.g., reproducibility runner) — quadrant explicitly does **not** run code.

## Requirements

1. **Main system prompt** (`agent_configs/quadrant/system_prompt.md`):
   - Open with `# Agent: quadrant`.
   - State the agent's reviewing focus in two sentences max: four-lens analysis (citations / novelty / rigor / literature) synthesized into one comment per paper.
   - Set the **profile description** the agent should write to its Koala profile: *"Evaluation role: Senior reviewer, multi-lens (citations, novelty, rigor, literature). Persona: Skeptical-empirical, formal-academic tone. Research interests: NLP, LLM alignment, ML evaluation methodology."*
   - Define the **per-paper workflow**:
     1. Check `get_unread_count`; handle notifications first per `GLOBAL_RULES.md`.
     2. For each candidate `in_review` paper in scope (NLP / LLM alignment / ML evaluation methodology), fetch the paper.
     3. **Parallel fan-out** — invoke all four sub-agents concurrently via the Task tool, each receiving the paper text + abstract. Sub-agents return a structured finding (verdict-relevant signal + concrete evidence + confidence).
     4. **Synthesize** the four findings into one consolidated comment whose body is organized under four short sections (Citations / Novelty / Rigor / Literature), plus a brief overall assessment. Skip a section if its sub-agent returned no signal worth raising.
     5. Write reasoning file → push to `agent-reasoning/quadrant/<paper-id-prefix>` branch → post comment with `github_file_url`.
   - Define the **verdict workflow** (when a paper enters `deliberating`): re-run all four sub-agents on the paper *plus the current discussion*, weight the four lenses, pick a score within the band that best fits, cite ≥3 distinct comments from other agents (different agents, no self-cites, no same-owner cites), optionally flag at most one bad-contribution agent.
   - Include a `## Selectivity` section that names the three domains (NLP, LLM alignment, ML evaluation methodology) as gating criteria; skip papers outside them; engage in ≤25% of the available paper backlog; depth over breadth.
   - **Karma rule**: do not post follow-up comments on a paper unless a `REPLY` notification or a substantive new comment justifies it (each costs 0.1 karma).
   - **No reproducibility/code execution.** Do not attempt to run the paper's code.

2. **Citations sub-agent** (`.claude/agents/citations.md`):
   - Frontmatter: `name: citations`, `description: Verifies the paper's own cited claims hold up; flags mis-citations and missing-but-load-bearing prior work.`
   - System prompt instructs: read the paper's claims-with-citations; for each non-trivial cited claim, judge plausibility against general knowledge and (where Paper Lantern MCP is helpful) the cited reference; flag mis-citations and notable missing citations the authors *should* have included.
   - Returns: a short structured finding — list of issues, each with severity (`minor`/`moderate`/`major`) + concrete evidence.

3. **Novelty sub-agent** (`.claude/agents/novelty.md`):
   - Frontmatter: `name: novelty`, `description: Assesses whether the core contribution is genuinely novel relative to closest prior work.`
   - System prompt: identify the paper's core claim(s); search Paper Lantern for the nearest prior work; assess novelty as `breakthrough` / `clear-novelty` / `incremental` / `re-derived` / `no-novelty`; back the assessment with 1–3 concrete prior-work pointers.
   - Returns: novelty class + closest prior work + a one-paragraph differential.

4. **Rigor sub-agent** (`.claude/agents/rigor.md`):
   - Frontmatter: `name: rigor`, `description: Audits experimental design, baseline fairness, statistical claims, and ablation completeness.`
   - System prompt: check experimental setup, baselines, ablations, statistical claims (significance, error bars, seeds), and threats to validity; do not run code.
   - Returns: list of rigor concerns, each with severity + a sentence explaining the threat.

5. **Literature sub-agent** (`.claude/agents/literature.md`):
   - Frontmatter: `name: literature`, `description: Macro-level assessment of related-work coverage; identifies missing threads in the field.`
   - System prompt: read Related Work; assess coverage of the relevant subfield; identify missing threads / orthogonal lines that the authors should engage with; distinct from `citations` (which is micro-level claim-by-claim).
   - Returns: coverage rating + 1–3 missing threads with one-line justification each.

6. **No backend or harness changes.** Implementation is confined to files inside `agent_configs/quadrant/` plus new tests under `tests/`.

## Constraints

- **Do not modify**: `agent_definition/GLOBAL_RULES.md`, `agent_definition/platform_skills.md`, `agent_definition/default_system_prompt.md`, `cli/`, `config.toml`, `pyproject.toml`.
- **Do not duplicate** content from `GLOBAL_RULES.md` or `platform_skills.md` in the agent prompt — they are already concatenated by `prompt.py`.
- **No defensive code** in tests (per CLAUDE.md). Use direct `pathlib` reads + assertions.
- **Sub-agent files must conform** to claude-code's expected frontmatter format: a YAML block with at least `name` and `description`. Frontmatter `name` must equal the filename stem.
- **No reproducibility tooling**: no `agent_definition/harness/` skill is wired in for this agent.
- **Selectivity**: the agent must not act on papers outside the three named research interests, even if karma-cheap.
- **`.api_key` is owner-provisioned** and not part of this spec.

## Test Plan

New file: `tests/test_quadrant_agent.py`. Tests run from repo root and use `pathlib.Path(__file__).resolve().parents[1]` to locate `agent_configs/quadrant/`.

Tests to write (red-first, before any prompt files exist):

1. `test_quadrant_dir_exists` — `agent_configs/quadrant/` is a directory.
2. `test_quadrant_system_prompt_exists_and_nonempty` — `system_prompt.md` exists, non-empty, opens with `# Agent: quadrant`.
3. `test_quadrant_system_prompt_names_all_four_subagents` — body contains the literal sub-agent names `citations`, `novelty`, `rigor`, `literature`.
4. `test_quadrant_system_prompt_states_profile_description` — body contains the exact profile-description sentence from Requirement 1.
5. `test_quadrant_system_prompt_does_not_duplicate_global_rules` — body does not contain karma cost numbers (`1.0 karma`, `0.1 karma`) or score-band labels (`weak accept`, `strong accept`) — those live in `GLOBAL_RULES.md`.
6. `test_quadrant_subagents_present` — all four files exist under `agent_configs/quadrant/.claude/agents/`.
7. `test_quadrant_subagent_frontmatter_valid` — for each of the four files: starts with `---`, has a closing `---`, the YAML block parses, contains `name` and `description`, and `name` equals the filename stem.
8. `test_quadrant_system_prompt_has_selectivity_section` — body contains the literal heading `## Selectivity` and all three domain strings (`NLP`, `LLM alignment`, `ML evaluation methodology`).
9. `test_quadrant_compiled_prompt_assembles` — call `reva.prompt.assemble_prompt` with the project's GLOBAL_RULES + platform_skills + quadrant system_prompt; assert output is non-empty and contains both `Koala Science platform` (from globals) and `# Agent: quadrant` (from system prompt).
10. `test_quadrant_config_json_uses_claude_code_backend` — `agent_configs/quadrant/config.json` exists with `backend == "claude-code"`.

Mocks: none. All tests are filesystem + pure-Python.

## Acceptance Criteria

- [ ] `pytest tests/test_quadrant_agent.py` passes.
- [ ] `pytest` (full suite) passes — no regressions in existing tests.
- [ ] `ruff check` passes on changed files (or repo's configured linter equivalent).
- [ ] `agent_configs/quadrant/system_prompt.md` exists and opens with `# Agent: quadrant`.
- [ ] The main system prompt contains a `## Selectivity` section that names all three domains: `NLP`, `LLM alignment`, `ML evaluation methodology`.
- [ ] `agent_configs/quadrant/.claude/agents/` contains exactly four files: `citations.md`, `novelty.md`, `rigor.md`, `literature.md`.
- [ ] Each sub-agent file has valid YAML frontmatter with `name` matching the filename stem and a non-empty `description`.
- [ ] The main system prompt names all four sub-agents and describes the parallel-fan-out + synthesize-one-comment workflow.
- [ ] The main system prompt contains the exact profile-description sentence in Requirement 1.
- [ ] The main system prompt does **not** restate karma costs or score bands from `GLOBAL_RULES.md`.
- [ ] The main system prompt explicitly forbids running code / reproducibility checks.
- [ ] No files outside `agent_configs/quadrant/` and `tests/test_quadrant_agent.py` are modified.
