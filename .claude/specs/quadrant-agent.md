# Spec: Quadrant — five-sub-agent reviewing agent

## Goal
Build one Koala-competition reviewing agent named `quadrant` that processes each in-scope paper through five claude-code sub-agents — an `extractor` that produces a structured digest, plus four parallel lens sub-agents (citations, novelty, rigor, literature) that consume the digest — then synthesizes their findings into a single consolidated comment per paper and a calibrated verdict.

## Context

### Relevant files
- `agent_configs/quadrant/` — the agent's working directory at runtime (cwd of the claude-code process). Created by `uv run reva create --name quadrant --backend claude-code` *outside* this spec's scope; the spec implementation populates the contents.
- `agent_configs/quadrant/system_prompt.md` — the hand-authored main-agent prompt. Concatenated with `agent_definition/GLOBAL_RULES.md` and `agent_definition/platform_skills.md` by `cli/reva/prompt.py:assemble_prompt` to form the runtime CLAUDE.md.
- `agent_configs/quadrant/.claude/agents/{extractor,citations,novelty,rigor,literature}.md` — Claude Code sub-agent definitions. Each is a markdown file with frontmatter (`name`, `description`, optional `tools`) plus a system-prompt body. claude-code automatically discovers `.claude/agents/*.md` from cwd, so no harness changes are needed.
- `agent_definition/GLOBAL_RULES.md` — platform-wide rules (read-only here). Defines karma economics, comment shape, verdict rules, score bands, moderation policy, branch policy for reasoning files. **Do not restate any of this in the agent prompt.**
- `agent_definition/platform_skills.md` — points the agent at `{KOALA_BASE_URL}/skill.md` for live MCP/API docs. The compiled prompt already includes this; the agent prompt should not duplicate.
- `cli/reva/backends.py:44` — confirms claude-code launches with `--mcp-config` for Paper Lantern; the Koala MCP key is provided via `.api_key` environment variable.
- `tests/test_cli.py` — pattern for prompt-assembly and agent-config tests. Tests for quadrant follow the same `pathlib`-based structural-check style.

### Current behavior
The agent is fully implemented and has been deployed once on SLURM. This spec captures the consolidated current design, including evolutions made post-initial-implementation: the `extractor` sub-agent, the comment-count gate, the tone-and-standards section, Strengths + Recommendations in the synthesis, and a hard rule against Task-tool bypass.

### How this fits
This is one of up to three agents the user may register under their OpenReview ID. It uses one slot. Other slots remain free for future, complementary agents (e.g., reproducibility runner) — quadrant explicitly does **not** run code.

## Requirements

1. **Main system prompt** (`agent_configs/quadrant/system_prompt.md`):
   - Open with `# Agent: quadrant`.
   - State the agent's reviewing focus in two sentences max: digest produced by the `extractor` feeds four-lens analysis (citations / novelty / rigor / literature) synthesized into one comment per paper.
   - Set the **profile description** the agent should write to its Koala profile: *"Evaluation role: Senior reviewer, multi-lens (citations, novelty, rigor, literature). Persona: Skeptical-empirical, formal-academic tone. Research interests: NLP, LLM alignment, ML evaluation methodology."*
   - Define the **per-paper workflow**:
     1. Check `get_unread_count`; handle notifications first per `GLOBAL_RULES.md`.
     2. Filter `in_review` candidates by **both** scope (NLP / LLM alignment / ML evaluation methodology) **and** the comment-count gate (see below).
     3. Fetch the paper (full text + abstract).
     4. **Extract, then fan out** — invoke `extractor` first via the Task tool and wait for its digest. Then invoke the four lens sub-agents concurrently via the Task tool, each receiving the digest as primary input and the raw paper text as a verification fallback. Sub-agents return structured findings (signal + concrete evidence + confidence).
     5. **Synthesize** the five outputs into one consolidated comment whose body has four parts: **Strengths** (one or two sentences naming concrete contributions, required even when overall is negative), **Citations / Novelty / Rigor / Literature** (four short critical sections from the four lens findings — skip a section if its sub-agent returned no signal worth raising), **Recommendations** (1–3 actionable items each tied to a limitation raised in one of the four critical sections), and a brief **Overall assessment**.
     6. Write reasoning file → push to `agent-reasoning/quadrant/<paper-id-prefix>` branch → post comment with `github_file_url`.
   - Include a **CRITICAL hard rule** in step 4 forbidding the orchestrator from `Read`-ing `.claude/agents/*.md` and executing the sub-agents' checks inline. Sub-agent dispatch via the Task tool is non-negotiable — the only exception is a tool-level hard failure, in which case the orchestrator may retry once before any fallback.
   - Define the **verdict workflow** (when a paper enters `deliberating`): re-run `extractor` with the paper *plus the current discussion* appended, then re-run the four lens sub-agents on the refreshed digest; weight the four lenses (rigor and novelty typically dominate; citations and literature tilt within a band rather than across bands); pick a score within the band that best fits; cite ≥3 distinct comments from other agents (different agents, no self-cites, no same-owner cites); optionally flag at most one bad-contribution agent.
   - Include a `## Selectivity` section that names the three domains (NLP, LLM alignment, ML evaluation methodology) as gating criteria; skip papers outside them; engage in ≤25% of the available paper backlog; depth over breadth.
   - Include a `## Comment-count gate` section that defines a soft sweet-spot of 1–3 existing other-agent top-level comments and explicitly handles three buckets: **0 comments** (skip by default — verdict-citation supply is unreliable), **1–3 comments** (preferred zone — discussion is forming, citation supply plausible), **≥4 comments** (avoid — per-credit karma `N / (K · c)` shrinks; override only on exceptional topical fit). Frame as a soft target, combinable with topical fit and recency.
   - Include a `## Tone and standards` section covering: formal academic language; evidence-based judgments only (every critique points at a quote, table, figure, citation, or absence); balanced critique with concrete strengths even in negative reviews; constructive framing (every limitation pairs with a recommendation in the synthesis or is explicitly flagged un-actionable); cross-discipline consistency across NLP, alignment, and evaluation-methodology submissions; ethics, originality, and disclosure (undisclosed dataset provenance or licensing, missing IRB / consent statements, plagiarism signals, reused figures/text without attribution).
   - **Karma rule**: do not post follow-up comments on a paper unless a `REPLY` notification or a substantive new comment justifies it (each costs 0.1 karma).
   - **No reproducibility/code execution.** Do not attempt to run the paper's code.

2. **Extractor sub-agent** (`.claude/agents/extractor.md`):
   - Frontmatter: `name: extractor`, `description: Produces a structured digest of the paper that the citations, novelty, rigor, and literature sub-agents consume as their primary input.`
   - Runs **before** the four lens sub-agents; its output is their primary input. Lens sub-agents fall back to the raw paper text only to verify a specific quote, table, or appendix item.
   - Output is a structured digest with six markdown sections in this order: **Header** (title, authors, domain tag, one-line gist); **Core claims** (for the novelty lens); **Methods and experimental setup** (for the rigor lens); **Cited claims** (for the citations lens); **Related-work positioning** (for the literature lens); **Open questions and verification hooks**.
   - Returns: a digest (markdown), not an evaluative finding. Faithful reduction only — no scoring, judging, or recommending. Does not invoke the four lens sub-agents itself.
   - In the verdict phase, accepts the discussion appended to the paper text as additional context for refreshing the digest.

3. **Citations sub-agent** (`.claude/agents/citations.md`):
   - Frontmatter: `name: citations`, `description: Verifies the paper's own cited claims hold up; flags mis-citations and missing-but-load-bearing prior work.`
   - System prompt instructs: take the digest's *Cited claims* section as canonical input; for each non-trivial cited claim, judge plausibility against general knowledge and (where Paper Lantern MCP is helpful) the cited reference; flag mis-citations and notable missing citations the authors *should* have included.
   - Returns: a short structured finding — list of issues, each with severity (`minor`/`moderate`/`major`) + concrete evidence + an overall summary line + confidence.

4. **Novelty sub-agent** (`.claude/agents/novelty.md`):
   - Frontmatter: `name: novelty`, `description: Assesses whether the core contribution is genuinely novel relative to closest prior work.`
   - System prompt: identify the paper's core claim(s) starting from the digest's *Core claims* section; search Paper Lantern for the nearest prior work; assess novelty as `breakthrough` / `clear-novelty` / `incremental` / `re-derived` / `no-novelty`; back the assessment with 1–3 concrete prior-work pointers.
   - Returns: novelty class + closest prior work + a one-paragraph differential + confidence.

5. **Rigor sub-agent** (`.claude/agents/rigor.md`):
   - Frontmatter: `name: rigor`, `description: Audits experimental design, baseline fairness, statistical claims, and ablation completeness.`
   - System prompt: starting from the digest's *Methods and experimental setup* section, check experimental setup, baselines, ablations, statistical claims (significance, error bars, seeds), threats to validity (with domain-specific pitfall lists for NLP / language models, LLM alignment, and ML evaluation methodology), and results-presentation / discussion / ethics (figure legibility, discussion engagement with implied limitations, dataset provenance and consent disclosures, attribution of reused material). Does not run code.
   - Returns: list of rigor concerns, each with severity + category + a sentence explaining the threat, plus an overall rating and confidence.

6. **Literature sub-agent** (`.claude/agents/literature.md`):
   - Frontmatter: `name: literature`, `description: Macro-level assessment of related-work coverage; identifies missing threads in the field.`
   - System prompt: read the digest's *Related-work positioning* section; assess coverage of the relevant subfield; identify missing threads / orthogonal lines that the authors should engage with; distinct from `citations` (which is micro-level claim-by-claim).
   - Returns: coverage rating + 1–3 missing threads with one-line justification each + confidence.

7. **No backend or harness changes.** Implementation is confined to files inside `agent_configs/quadrant/` plus tests under `tests/`.

## Constraints

- **Do not modify**: `agent_definition/GLOBAL_RULES.md`, `agent_definition/platform_skills.md`, `agent_definition/default_system_prompt.md`, `cli/`.
- **Do not duplicate** content from `GLOBAL_RULES.md` or `platform_skills.md` in the agent prompt — they are already concatenated by `prompt.py`.
- **No defensive code** in tests (per CLAUDE.md). Use direct `pathlib` reads + assertions.
- **Sub-agent files must conform** to claude-code's expected frontmatter format: a YAML block with at least `name` and `description`. Frontmatter `name` must equal the filename stem.
- **No reproducibility tooling**: no `agent_definition/harness/` skill is wired in for this agent.
- **Selectivity is hard**; the agent must not act on papers outside the three named research interests, even if karma-cheap.
- **Comment-count gate is soft**; it can be overridden at the margin by topical fit, recency, and the depth-over-breadth principle.
- **Sub-agent dispatch is non-negotiable**: the orchestrator must not bypass the Task-tool dispatch by reading sub-agent definitions and running their checks inline.
- **`.api_key` is owner-provisioned** and not part of this spec.

## Test Plan

Test file: `tests/test_quadrant_agent.py`. Tests run from repo root and use `pathlib.Path(__file__).resolve().parents[1]` to locate `agent_configs/quadrant/`. All `pathlib` + pure-Python, no mocks.

Currently implemented:

1. `test_quadrant_dir_exists`
2. `test_quadrant_system_prompt_exists_and_nonempty` — opens with `# Agent: quadrant`.
3. `test_quadrant_system_prompt_names_all_four_subagents` — body names the four lens sub-agents. (Predates the addition of `extractor`; `SUBAGENT_NAMES` should be widened to all five.)
4. `test_quadrant_system_prompt_states_profile_description` — body contains the exact senior-reviewer profile sentence.
5. `test_quadrant_system_prompt_does_not_duplicate_global_rules` — body does not restate karma costs or score-band labels.
6. `test_quadrant_subagents_present` — the four lens files exist; should be widened to require `extractor.md`.
7. `test_quadrant_subagent_frontmatter_valid` — frontmatter check; should iterate all five sub-agents.
8. `test_quadrant_system_prompt_has_selectivity_section` — body contains `## Selectivity` and the three domain strings.
9. `test_quadrant_compiled_prompt_assembles` — `reva.prompt.assemble_prompt` produces non-empty output containing GLOBAL_RULES content + `# Agent: quadrant`.
10. `test_quadrant_config_json_uses_claude_code_backend`.

Tests still to add to fully cover this spec (currently absent):

- `test_quadrant_extractor_subagent_present_and_valid` — `extractor.md` exists with valid frontmatter (`name: extractor`).
- `test_quadrant_system_prompt_has_comment_count_gate` — body contains `## Comment-count gate` heading and the three bucket markers.
- `test_quadrant_system_prompt_has_tone_and_standards` — body contains `## Tone and standards` heading.
- `test_quadrant_system_prompt_synthesis_lists_strengths_and_recommendations` — synthesis-step body contains the literals `Strengths`, `Recommendations`, and `Overall assessment`.
- `test_quadrant_system_prompt_forbids_task_tool_bypass` — body contains the CRITICAL hard rule (the literal phrase forbidding `Read`-ing of `.claude/agents/*.md`).

## Acceptance Criteria

- [ ] `pytest tests/test_quadrant_agent.py` passes.
- [ ] `pytest` (full suite) passes — no regressions in existing tests.
- [ ] `agent_configs/quadrant/system_prompt.md` exists and opens with `# Agent: quadrant`.
- [ ] The main system prompt contains a `## Selectivity` section that names all three domains: `NLP`, `LLM alignment`, `ML evaluation methodology`.
- [ ] The main system prompt contains a `## Comment-count gate` section with the 0 / 1–3 / ≥4 buckets explained.
- [ ] The main system prompt contains a `## Tone and standards` section.
- [ ] `agent_configs/quadrant/.claude/agents/` contains exactly five files: `extractor.md`, `citations.md`, `novelty.md`, `rigor.md`, `literature.md`.
- [ ] Each sub-agent file has valid YAML frontmatter with `name` matching the filename stem and a non-empty `description`.
- [ ] The main system prompt names all five sub-agents and describes the **extract-then-fan-out** workflow with concurrent Task-tool dispatch of the four lenses.
- [ ] The main system prompt contains an explicit, prominently marked rule forbidding the orchestrator from inlining sub-agent work by reading `.claude/agents/*.md` directly.
- [ ] The synthesis step describes a body with **Strengths → Citations/Novelty/Rigor/Literature → Recommendations → Overall assessment**.
- [ ] The main system prompt contains the exact senior-reviewer profile-description sentence in Requirement 1.
- [ ] The main system prompt does **not** restate karma costs or score bands from `GLOBAL_RULES.md`.
- [ ] The main system prompt explicitly forbids running code / reproducibility checks.
