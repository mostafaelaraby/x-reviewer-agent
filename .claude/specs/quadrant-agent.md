# Spec: Quadrant — single-orchestrator reviewing agent

## Goal
Build one Koala-competition reviewing agent named `quadrant` that, for each in-scope paper, produces one evidence-backed comment in a fixed four-section structure (Strengths / Concerns / Recommendations / Overall) and a calibrated verdict when the paper enters its deliberation window. The agent is a single claude-code orchestrator with **no sub-agents**; the four-lens analysis (citations / novelty / rigor / literature) lives as an inline checklist that the orchestrator applies before drafting.

## Context

### Relevant files
- `agent_configs/quadrant/` — the agent's working directory at runtime (cwd of the claude-code process). Created by `uv run reva create --name quadrant --backend claude-code` *outside* this spec's scope; the spec implementation populates the contents.
- `agent_configs/quadrant/system_prompt.md` — the hand-authored agent prompt. Concatenated with `agent_definition/GLOBAL_RULES.md` and `agent_definition/platform_skills.md` by `cli/reva/prompt.py:assemble_prompt` to form the runtime CLAUDE.md.
- `agent_configs/quadrant/.claude/agents/` — **must remain empty**. The single-orchestrator design has no sub-agent dispatch; an empty directory is fine, leftover sub-agent files are not.
- `agent_definition/GLOBAL_RULES.md` — platform-wide rules (read-only here). Defines karma economics, comment shape, verdict rules, score bands, moderation policy, branch policy for reasoning files. **Do not restate any of this in the agent prompt.**
- `agent_definition/platform_skills.md` — points the agent at `{KOALA_BASE_URL}/skill.md` for live MCP/API docs. The compiled prompt already includes this; the agent prompt should not duplicate.
- `cli/reva/backends.py:44` — confirms claude-code launches with `--mcp-config` for Paper Lantern; the Koala MCP key is provided via the `COALESCENCE_API_KEY` environment variable loaded from `.api_key`.
- `tests/test_cli.py` — pattern for prompt-assembly and agent-config tests.

### Current behavior
The agent is implemented in this single-orchestrator form. An earlier five-sub-agent design (extractor + four lens sub-agents) was retired: the inter-process orchestration cost exceeded its quality benefit within the competition wall-clock budget, and per-paper wall time exceeded the harness's `SESSION_TIMEOUT`, preventing any paper from being completed end-to-end.

### How this fits
This is one of up to three agents the user may register under their OpenReview ID. It uses one slot. Other slots remain free for future, complementary agents (e.g., reproducibility runner) — quadrant explicitly does **not** run code.

## Requirements

1. **Main system prompt** (`agent_configs/quadrant/system_prompt.md`):
   - Open with `# Agent: quadrant`.
   - State the agent's reviewing focus in two sentences max: single orchestrator, four-lens checklist applied inline, one comment per paper, calibrated verdict in the deliberation window.
   - Set the **profile description** the agent should write to its Koala profile: *"Evaluation role: Senior reviewer (citations, novelty, rigor, literature). Persona: Skeptical-empirical, formal-academic tone. Research interests: NLP, LLM alignment, ML evaluation methodology."*
   - Define the **per-paper workflow**:
     1. Check `get_unread_count`; handle notifications first per `GLOBAL_RULES.md`.
     2. List `in_review` candidates, filter to scope + comment-count gate; prefer the freshest 1-comment paper for first-proposer advantage.
     3. Fetch the PDF; extract text via `pypdf` (with `offset`/`limit` for long PDFs); fall back to abstract + existing-comments-only mode with a `[abstract-only]` header tag if extraction fails. Use Paper Lantern MCP for novelty lookups.
     4. Apply the four-lens checklist mentally before drafting: citations / novelty / rigor / literature. Each lens carries 1–2 evidence-backed observations; domain-specific pitfall lists for NLP, alignment, and eval-methodology are baked into the checklist.
     5. Draft one consolidated comment with the **fixed four-section structure**: **Strengths** (1–2 sentences, required), **Concerns** (2–4 evidence-backed issues citing specific tables/figures/page numbers/quotes), **Recommendations** (1–3 actionable items each tied to a stated concern), **Overall** (1–2 sentences positioning the paper in its likely verdict band, no numeric score).
     6. Write a reasoning markdown file (the comment + 2–4 supporting quotes with locations) → push to `agent-reasoning/quadrant/<paper-id-prefix>` → verify blob URL is reachable → post comment with `github_file_url`.
     7. Loop.
   - Define the **verdict workflow** (when a `PAPER_DELIBERATING` notification arrives): re-read the paper and the current discussion, apply a deterministic novelty × rigor → band rubric, refine within ±0.5 based on citations/literature signals, cite ≥3 distinct other-agent comments, optionally flag at most one bad-contribution agent.
   - Include a `## Selectivity` section that names the three domains (NLP, LLM alignment, ML evaluation methodology) as gating criteria; skip papers outside them.
   - Include a `## Comment-count gate` section defining the soft sweet-spot of 1–3 other-agent top-level comments. Within the band, prefer 1-comment papers (first-proposer advantage); explicitly handle 0 (skip), 1 (preferred), 2–3 (fine), ≥4 (avoid). Backlog cap: ≤25%.
   - Include a `## Standards` (or equivalent) section covering: formal academic language; evidence-only critique citing specific tables/figures/page numbers/quotes; constructive framing pairing concerns with recommendations; cross-discipline consistency; no reproducibility / code execution; ethics, originality, and disclosure flags.
   - **Karma rule**: do not post follow-up comments on a paper unless a `REPLY` notification or a substantive new comment justifies it.
   - **No reproducibility/code execution.** Do not attempt to run the paper's code.

2. **No sub-agents.** `.claude/agents/` must contain no `*.md` files. The four-lens analysis is an inline checklist in the orchestrator's prompt, not a multi-process fan-out.

3. **No backend or harness changes.** Implementation is confined to files inside `agent_configs/quadrant/` plus tests under `tests/`.

## Constraints

- **Do not modify**: `agent_definition/GLOBAL_RULES.md`, `agent_definition/platform_skills.md`, `agent_definition/default_system_prompt.md`, `cli/`.
- **Do not duplicate** content from `GLOBAL_RULES.md` or `platform_skills.md` in the agent prompt — they are already concatenated by `prompt.py`.
- **No defensive code** in tests. Use direct `pathlib` reads + assertions.
- **No reproducibility tooling**: no `agent_definition/harness/` skill is wired in for this agent.
- **Selectivity is hard**; the agent must not act on papers outside the three named research interests.
- **Comment-count gate is soft**; it can be overridden at the margin by topical fit, recency, and the depth-over-breadth principle.
- **`.api_key` is owner-provisioned** and not part of this spec.
- **No sub-agents.** A future contributor adding `.claude/agents/*.md` files should also re-introduce dispatch logic and update tests; the test suite enforces the empty-directory invariant.

## Test Plan

Test file: `tests/test_quadrant_agent.py`. Tests run from repo root and use `pathlib.Path(__file__).resolve().parents[1]` to locate `agent_configs/quadrant/`. All `pathlib` + pure-Python, no mocks.

1. `test_quadrant_dir_exists`
2. `test_quadrant_system_prompt_exists_and_nonempty` — opens with `# Agent: quadrant`.
3. `test_quadrant_system_prompt_names_all_four_lenses` — body mentions all four lens names (citations, novelty, rigor, literature).
4. `test_quadrant_system_prompt_states_profile_description` — body contains the exact senior-reviewer profile sentence.
5. `test_quadrant_system_prompt_does_not_duplicate_global_rules` — body does not restate karma costs or score-band labels.
6. `test_quadrant_has_no_subagents` — `.claude/agents/` is empty (or missing).
7. `test_quadrant_system_prompt_has_selectivity_section` — body contains all three domain strings.
8. `test_quadrant_system_prompt_describes_comment_structure` — body contains the literals `Strengths`, `Concerns`, `Recommendations`, `Overall`.
9. `test_quadrant_compiled_prompt_assembles` — `reva.prompt.assemble_prompt` produces non-empty output containing GLOBAL_RULES content + `# Agent: quadrant`.
10. `test_quadrant_config_json_uses_claude_code_backend`.

## Acceptance Criteria

- [ ] `pytest tests/test_quadrant_agent.py` passes.
- [ ] `pytest` (full suite) passes — no regressions in existing tests.
- [ ] `agent_configs/quadrant/system_prompt.md` exists and opens with `# Agent: quadrant`.
- [ ] `agent_configs/quadrant/.claude/agents/` contains no `*.md` files.
- [ ] The system prompt contains the exact senior-reviewer profile-description sentence.
- [ ] The system prompt mentions all four lenses (citations, novelty, rigor, literature) as a checklist, not as sub-agent dispatch targets.
- [ ] The system prompt names the three in-scope domains.
- [ ] The system prompt defines the four-section comment structure: Strengths / Concerns / Recommendations / Overall.
- [ ] The system prompt defines the comment-count gate with explicit handling of 0 / 1 / 2–3 / ≥4 buckets.
- [ ] The system prompt defines a verdict workflow with a deterministic novelty × rigor → band rubric.
- [ ] The system prompt does **not** restate karma costs or score bands from `GLOBAL_RULES.md`.
- [ ] The system prompt explicitly forbids running code / reproducibility checks.
