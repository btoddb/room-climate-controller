# Ability to adjust target temps, right on main card

**Status:** in progress
**Touches:** card-ux

## Goal

I'd like up/down arrow buttons on the main card to adjust the target temperatures for each device the room supports.

## Behavior

Numbered, testable statements. Mark each as a **constraint** (must) or
**suggestion** (open to alternatives) when it isn't obvious.

1. **constraint** press the up arrow, it raises the target temp for its device 1 degree
2. **constraint** press the down arrow, it lowers the target temp for its device 1 degree
3. **constraint** raising/lowering a target temp must be constrained by the device's temp range
3. **constraint** raising/lowering a target temp must adhere to all rules for setting temps.  For instance, if lowering the target temp for a cooling device, it must stay above the heating target temp
3. **constraint** target temps can be changed regardless of the room's toggles

## UI (only if applicable)

I would like the arrows represented by triangles, one above the other, and the one on bottom is upside down.  The one on top raises temps, the one on bottom lowers temps.  I'd like the arrows in a column by themselves to the left of the Fan Ovr toggle.  Each set of arrows are aligned vertically with other device arrows.

## Out of scope

N/A

## Acceptance criteria

How we'll know it's done — concrete checks (engine test cases, a behavior to
observe in the running app, etc.).

- [ ] up arrows raise their device's target temp, but they do not cause target temp to go outside device's temp range
- [ ] down arrows lower their device's target temp, but they do not cause target temp to go outside device's temp range
- [ ] changing cooling target must always stay above heating target temp
- [ ] changing heating target must always stay below cooling target temp
- [ ] changing target temps using these arrows does not effect toggles for the devices
