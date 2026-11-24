# Scientific research Skill suite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Produce ten self-contained competition Skills with real deterministic helpers, useful examples, and reproducible local verification.

**Architecture:** A small portable Python helper library handles source anchors, protected facts and contract checking. Task-specific instructions and helpers add bibliography, graph, PDF and TeX behavior. Each submission receives physical copies of only its needed resources.

**Tech Stack:** Python 3 standard library; optional available PDF/document parsers and actual runtime executables. Official Playground CLI for packaging.

**Spec:** `D:\Bohrium-Playground\competition\docs\参赛开发方案.md`, approved by the user in this chat on 2026-11-24.

## Global Constraints

- At most 50 UTF-8 text files, 500 KB per file and 2 MB per Skill; no symlinks.
- Runtime: `/input/case.json`, actual `task.md`, `/app/work`, `/app/output`, `/skills/weekly-skill`.
- Preserve `case_id` and every original `output_contract` field; never present development examples as official cases or scores.
- Official case budget: 64 requests, 900 seconds, 16384 tokens per response including reasoning.
- Final development and submission files live on D:; this workspace's work directory is temporary authoring scratch only.
- No repository publication or formal attempt during this implementation until scoring-route ambiguities are resolved and outputs are reviewed.

## Review Focus

- An unfamiliar output-contract shape must be reported as unvalidated, not silently passed.
- A missing source, stale hash, unsupported format or invented evidence quote must fail explicitly.
- Bilingual outputs contain repeated numbers legitimately; audit translated spans rather than whole bilingual containers.
- Similar references/entities with conflicting identity fields must not be automatically merged.
- Failed or missing OCR/TeX tools must not produce a success claim or reuse a stale artifact.

### Task 1: Portable evidence and validation helpers

Files: `shared/research_tools.py`, `tests/test_research_tools.py`.

Interfaces: `extract_document(path: Path) -> dict`, `audit_text(before: str, after: str) -> dict`, `audit_edits(document: dict, edits: list) -> dict`, `check_contract(contract: object, result: dict) -> dict`, `check_evidence(documents: list, entries: list) -> dict`.

- [x] Write tests for line/page anchors, immutable numbers/citations/math, missing/duplicate edit segments, unknown contract shapes, required nested fields, invalid quotes and source changes.
- [x] Run unittest before implementation and observe missing-module failure.
- [x] Implement the stated interfaces and CLI commands using standard-library fallbacks and optional installed parsers.
- [x] Run the tests and inspect every failure before recording completion.

### Task 2: Task-specific scientific helpers

Files: `shared/structured_tools.py`, `shared/document_tools.py`, `tests/test_specialists.py`.

Interfaces: `deduplicate(records: list) -> dict`, `validate_graph(graph: dict) -> dict`, `query_graph(graph: dict, subject: str, relation: str|None) -> dict`, `lint_assertions(assertions: list) -> dict`, `audit_tex(project: Path) -> dict`, `build_tex(project: Path, main: str, out: Path, engine: str|None, timeout: int) -> dict`, `extract_pdf_layout(path: Path) -> dict`.

- [x] Write tests for conflicting DOI identities, graph dangling links/query evidence, compound/unsupported assertions, undefined TeX references, missing compiler and stale-output isolation.
- [x] Observe failures, implement helpers, then verify the full suite.
- [x] Add a generated two-column PDF development fixture and verify actual reading order and anchors if the optional local parser is available; label OCR as untested if no engine exists.

### Task 3: Ten independent Skill packages

Files: `build_suite.py`, `skills/<skill>/SKILL.md`, `references/workflow.md`, needed `scripts/*.py`, `examples/*`.

Consumes: Task 1 and Task 2 helpers. Produces: ten portable source packages and a manifest mapping task IDs to package names.

- [x] Create task-specific workflows for polishing, notes, translation, bibliography, methods, introduction, parsing, assertions, graph, and TeX.
- [x] State exact runtime adaptation, honest early saves, bounded tool use, provenance, task-specific checks and failure recovery.
- [x] Include a minimal input and clearly labeled illustrative invocation/output in each package; do not include formal answers or fake GitHub links.
- [x] Verify resource limits, UTF-8, relative references, no symlinks and valid skill frontmatter for all ten.

### Task 4: Independent forward-test and final review

- [x] Create isolated development requests for the first two Skills and run them with an independent agent under the Skill Creator forward-test guidance; retain raw outputs and actual checks, without claiming official-model equivalence.
- [x] Dispatch one fresh whole-suite reviewer as required by executing-plans. No credentials or unrelated histories enter review context.
- [x] Fix material findings with reproducing tests and rerun the affected suite.

### Task 5: D-drive deployment and official dry-runs

- [x] Copy tested source packages and tests into `D:\Bohrium-Playground\competition` and the ten package folders into `D:\Bohrium-Playground\submissions`.
- [x] Run official skill validation and `submit --dry-run` with the genuine native Codex log for each task, using explicit output locations outside the submitted Skill folders.
- [x] Inspect packaged files for leaked credentials, incorrect content, missing resources and accidental formal examples; report actual failures rather than calling a dry-run an evaluation.
- [x] Save a concise status report and verification manifest to outputs, with D-drive copies. Record that no final scores exist until real evaluations are available.

## Execution record

The user explicitly said to start after approving the design. Implementation therefore proceeds continuously in this chat, without another handoff question.
This is a new directory, not a shared branch or existing checkout. A local development branch may be initialized on D:; no worktree, commit identity change, push, or publication is required. Native Windows test commands and a simple progress ledger replace the skill's POSIX-only git helper scripts where those helpers assume an existing repository.
