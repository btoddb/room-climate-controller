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

`custom_components/dreo/` is a **vendored third-party integration** kept only for
local testing — do not modify it.

## Requirements

Functional behavior is specified in [requirements/](requirements/) — start at
[requirements/README.md](requirements/README.md). The living spec under
`requirements/spec/` always reflects shipped behavior; new work starts in
`requirements/proposals/`. When something ships, fold it into the spec.


## Implementation details

- **Python version:** target python version 3.14 or newer
- **Ruff Formatting:** format all code according to the ruff formatting rules
- **Ruff Linting:** Ensure coding decisions are made with ruff linting rules in mind

## Key dev commands

- **Run HA locally:** `scripts/develop` (launches HA against `config/`; note no
  Node/npm is preinstalled in this devcontainer).
- **Lint:** `scripts/lint` (ruff).
- **Engine unit tests (no HA needed):**
  `python3 custom_components/room_climate_controller/tests/test_engine.py`
- **Validate manifest/HACS:** `python3 -m script.hassfest` and the
  `.github/workflows/validate.yml` workflow.
- **Build the card:** `scripts/deploy.sh` builds, bumps the version, and copies
  into `www/`. Edit the TypeScript source at
  `custom_components/room_climate_controller/card/src/*.ts` — never hand-edit the
  generated `www/*.js` bundle. (Card-specific guidance lives in that folder's
  `CLAUDE.md`.)


## Git workflow

- **Do NOT work on `main`.** Create a feature branch.
- The project prefers **linear history** — rebase/squash rather than merge.
- Don't commit `config/.storage`, the HA database, or `card/node_modules`.
