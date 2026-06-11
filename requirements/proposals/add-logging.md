# Logging

**Status:** shipped — folded into [requirements/spec/logging.md](../spec/logging.md)
**Touches:** Backend code, no UI

## Goal

Currently there isn't a good way to troubleshoot Room Climate Controller (RCC).  I want to add log messages throughout the code that will give a picture of what happened if I think there's a problem.  I want to be able to find them easily in HA's raw log messages by filtering.

## Behavior

**constraint** the log message should be formatted such that I can easily filter using HA's log viewer.  Specifically I should be able to easily see all messages logged by room climate controller.  I should also be able to limit the messages to a specific room, sensor, device, etc.

Log messages on these events at INFO level:
1. **constraint** if RCC notices a room's temperature changes
2. **constraint** if RCC notices a room's humidity changes
3. **constraint** when a profile is edited, activated, or applied, log the settings
4. **constraint** when a toggle is changed
6. **constraint** when a new room is created, it's devices are changed, or any settings are changed
7. **suggestion** add any other logs you think I missed

## UI (only if applicable)

No changes to the card

## Out of scope

Logging UI events

## Acceptance criteria

I'm able to see over time how a room's climate controller behaves.  Get a clear picture of what is causing devices to turn on/off.
