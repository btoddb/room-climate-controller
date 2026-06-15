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