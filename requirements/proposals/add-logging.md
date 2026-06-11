# Logging

**Status:** in progress
**Touches:** Backend code, no UI

## Goal

Currently there isn't a good way to troubleshoot Room Climate Controller (RCC).  I want to add log messages throughout the code that will give a picture of what happened if I think there's a problem.  I want to be able to find them easily in HA's raw log messages by filtering.

## Behavior

Numbered, testable statements. Mark each as a **constraint** (must) or
**suggestion** (open to alternatives) when it isn't obvious.

**suggestion** the log message should look something like this.

Log messages on these events:
1. **constraint** if RCC notices a room's temperature changes
2. **constraint** if RCC notices a room's humidity changes
3. **constraint** when a profile is activated or applied
4. **constraint** when a toggle is changed
6. **constraint** when a new room is created, it's devices  are changed, or any settings are changed

## UI (only if applicable)

What changes on the card / dialogs. Reference existing UX rules by ID where relevant.

## Out of scope

What this explicitly does *not* change, to prevent scope creep.

## Acceptance criteria

How we'll know it's done — concrete checks (engine test cases, a behavior to
observe in the running app, etc.).

- [ ] …
- [ ] …
