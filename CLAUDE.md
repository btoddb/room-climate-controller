# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repo is a single Home Assistant **custom integration**, `room_climate_controller`
(HACS-installable), that does per-room climate control and scheduled daily climate
**profiles** entirely in-process — plus a companion Lit/TypeScript Lovelace card it
ships and auto-registers. The requirements live in [requirements/](requirements/).

The repo is based on the `integration_blueprint` dev scaffold: `config/` is a throwaway
HA instance for local testing, `scripts/` holds dev helpers, and `requirements.txt`
pins the HA/lint toolchain.

## Key dev commands

- **Run HA locally:** `scripts/develop` (launches HA against `config/`; note no
  Node/npm is preinstalled in this devcontainer).
- **Lint:** `scripts/lint` (ruff).
- **Engine unit tests (no HA needed):**
  `python3 custom_components/room_climate_controller/tests/test_engine.py`
- **Validate manifest/HACS:** `python3 -m script.hassfest` and the
  `.github/workflows/validate.yml` workflow.
- **Build the card:**
  `card/deploy.sh` to build, bump the version, and copy into `www/`). Edit
  `card/src/*.ts` — never hand-edit the generated `www/*.js` bundle.


## Git workflow

- **Do NOT work on `main`.** Create a feature branch.
- The project prefers **linear history** — rebase/squash rather than merge.
- Don't commit `config/.storage`, the HA database, or `card/node_modules`.
