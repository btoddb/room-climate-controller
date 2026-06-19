# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**These rules are non-negotiable — follow them exactly.**

## Project Overview

This repo is a single Home Assistant **custom integration**, `room_climate_controller`
(HACS-installable), that does per-room climate control and scheduled daily climate
**profiles** entirely in-process — plus a companion Lit/TypeScript Lovelace card it
ships and auto-registers.

The repo is based on the `integration_blueprint` dev scaffold: `config/` is a throwaway
HA instance for local testing, `scripts/` holds dev helpers, and `requirements.txt`
pins the HA/lint toolchain.

Every directory under `custom_components/` **except `room_climate_controller`** is a
**vendored third-party integration** kept only for local testing (currently
`custom_components/dreo/`). Never modify any of them. If any command — including
`scripts/lint` — leaves changes under one of these directories, revert them; never
commit a diff outside `room_climate_controller`.

## GitHub Workflow

`.github/workflows/claude.yml` selects the model per job, so each phase below
runs on the model named here automatically — you do not (and cannot) switch
models yourself mid-run:

- **New issue** opened/assigned → planning → **Opus**, which then hands off to…
- …**implementation** → **Sonnet**, *in the same workflow run*, but only if the
  plan had no open questions (see Planning below).
- **PR review** submitted → review → **Opus**
- **Follow-up comments** (issue or PR review comments) → **Sonnet**

The plan→implement handoff is a job dependency inside one run, not a re-trigger:
GitHub will not start a new workflow run from a comment the action posts with
`GITHUB_TOKEN`, so the pipeline is chained via `needs:` instead.

### Planning (Opus)
- For every new issue, Opus must read the codebase and generate a structural implementation plan before making any code changes.
- Ensure the plan is clear and outlines the required steps.
- **constraint** Opus must post the completed plan **as a comment on the issue** — this is the only thing that carries the plan to the implementation job.
- **constraint** Every plan comment must include the exact line `<!-- claude:plan -->` so it can be located later. A plan **revision** is posted as a **new** comment carrying the same marker — never silently rewrite history. The pipeline always uses the **most recent** `claude:plan` comment.
- **The latest plan comment is also the gate for auto-implementation:**
  - If you have **zero `[QUESTION]` items**, also include the exact line `<!-- claude:proceed -->`. The `implement` job finds the latest plan comment, sees this marker, and Sonnet implements the plan and opens the PR automatically — no human step required.
  - If you have **any `[QUESTION]` items**, do **not** include the proceed marker. Instead `@btoddb` in the comment so they are notified to answer. Implementation stays parked until a newer plan comment is posted with the proceed marker.

### Implementation (Sonnet)
- Sonnet should execute the approved plan strictly.
- **constraint** **NEVER** work on main.  Create a new branch for the changes
- Implement the code and cut a Pull Request (PR) referencing the original issue

#### What Not to Commit
- Build artifacts, generated bundles, and compiled outputs (unless the project explicitly tracks them).
- Dependency and cache directories: `node_modules/`, `__pycache__/`, `.venv/`, and equivalents.
- OS-generated files (`.DS_Store`, `Thumbs.db`) and editor swap/lock files.

#### Security
- **constraint** Never commit secrets, API keys, credentials, `.env` files, or private config — not even in test or scratch branches.
- **constraint** Flag any security vulnerability (XSS, SQL injection, command injection, etc.) and fix it before reporting the task complete.

### Review (Opus)
- **constraint** On any new PR, Opus should perform a line-by-line review.
- Add specific, actionable comments in the PR.
- Stop, wait, and request explicit human approval before attempting any fixes or merges.
- **constraint** If you are asked to review a PR, **NEVER** make changes to the code base.  You are free to add comments with snippets of suggested code.

If you leave a comment on the PR, and it is more than just a comment, tag each comment with one of the following:
- [REQUIRED]: A critical issue that must be fixed before approval
- [QUESTION]: Asking for clarification on why an implementation was chosen
- [NIT]: Minor styling, naming choices, or optional micro-optimizations that won't hold up approval
- [PRAISE]: Highlighting particularly clean, clever, or well-written sections of code

## Implementation details

- **Python version:** target python version 3.14 or newer
- **Ruff Formatting:** format all code according to the ruff formatting rules
- **Ruff Linting:** Ensure coding decisions are made with ruff linting rules in mind

## Key dev commands

- **Run HA locally:** `scripts/develop` (launches HA against `config/`). It runs HA
  in the **foreground** with `--debug` and does not return — to verify a change,
  background it and read `config/home-assistant.log`. Node/npm *are* available in
  this devcontainer (Node feature); `scripts/develop` is unrelated to the card build.
- **Lint:** `scripts/lint` (ruff). It **rewrites files** (`ruff format` +
  `ruff check --fix`) — it is not a check-only command, so expect working-tree
  changes after it runs.
- **Engine unit tests (no HA needed):**
  `pytest custom_components/room_climate_controller/tests/`
- **Validate manifest/HACS:** `python3 -m script.hassfest` and the
  `.github/workflows/validate.yml` workflow.
- **Build the card:** `scripts/deploy.sh` builds, bumps the version, and copies
  into `www/`. Edit the TypeScript source at
  `custom_components/room_climate_controller/card/src/*.ts` — never hand-edit the
  generated `www/*.js` bundle. (Card-specific guidance lives in that folder's
  `CLAUDE.md`.)

## Versioning

There are **two independent version numbers** — never hand-edit either:

- **Integration:** `manifest.json` (`"version": "vX.Y.Z"` — the leading `v` is
  intentional). Bumped only by `scripts/create-release.sh`.
- **Card:** `card/package.json` (plain `X.Y.Z`). Bumped only by `scripts/deploy.sh`,
  which also syncs the console banner in `card/src/index.ts`.