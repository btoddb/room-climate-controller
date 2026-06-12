# Add reverse direction control for standalone ceiling fans

**Status:** in progress
**Touches:** climate-control, profiles, card-ux

## Goal

Ceiling fans can spin forward (summer, pushing cool air down) or reverse
(winter, drawing warm air up from the ceiling). This adds a per-room
**Fan reverse** toggle so the user can configure direction from the card,
have it applied on schedule via profiles, and see the current direction
reflected in the main card's Fan section.

## Behavior

1. **Auto-detect reversibility** — no config-flow toggle. A fan is considered
   reversible when its HA entity advertises `FanEntityFeature.DIRECTION` in
   `supported_features`, **or** when `"reverse"` appears in its `preset_modes`
   list (used by integrations such as Dreo that express direction as a preset
   rather than a native direction feature). Detection is live at evaluation
   time, not at platform setup.

2. Each room with a standalone fan gets a **Fan reverse** `switch.*` entity
   created unconditionally — detection at platform-setup time would race fan
   integrations that load later. The switch is inert for non-reversible fans.

3. When the fan is **reversible and running**, and its reported direction
   differs from the requested one (Fan reverse switch on → `reverse`, off →
   `forward`), the engine emits a set-direction command. For native-DIRECTION
   fans the controller calls `fan.set_direction`; for preset fans it calls
   `fan.set_preset_mode("reverse")` / `fan.set_preset_mode(<forward-preset>)`.

4. **Idempotence**: the command is suppressed when the reported direction
   already matches. An unknown / `None` direction never matches, so it emits.

5. Direction is applied **only while the fan is running**. When the fan must
   start and reverse in the same evaluation, turn-on precedes set-direction.
   A reverse request while the fan is off takes effect at the next turn-on.

6. **Non-reversible fans** never receive a direction command, even when the
   Fan reverse switch is on.

7. **Profiles** carry a `fan_reverse` field. Scheduled and explicit applies
   write the room's Fan reverse switch; the controller reacts per rule 3.

## UI

- **Settings dialog**: a **Reverse** toggle appears in the Fan section only
  when `rooms/list` reports `fan_reversible: true` for the room (UX-28).
- **Main card Fan section**: while a fan that reports a direction is running,
  the mode text appends the direction in parentheses — e.g. `50% (Reverse)`
  or `50% (Forward)`. "Off" stays plain (UX-29).
- **Profiles panel**: the Fan row includes a Reverse toggle when the fan is
  reversible (UX-21).

## Out of scope

- Direction control for A/C or heater companion fans.
- A config-flow option to mark a fan as reversible.

## Acceptance criteria

- [ ] Engine tests CC-22..CC-25 pass for both the native-DIRECTION path and
      the preset-mode path.
- [ ] `switch.<room>_fan_reverse` entity appears for every room with a
      standalone fan, regardless of the fan's capabilities.
- [ ] Toggling Fan reverse while the fan is running causes a `fan.set_direction`
      or `fan.set_preset_mode` service call within one evaluation cycle.
- [ ] No direction command is emitted when the fan is off or `use_fan` is off.
- [ ] Profiles: a profile with `fan_reverse=True` applied to a reversible fan
      turns on the Fan reverse switch; the fan spins in reverse on the next
      evaluation.
- [ ] Card (UX-28): Reverse toggle visible in settings dialog for reversible
      fans, absent for non-reversible fans.
- [ ] Card (UX-29): while the fan is running and reports a direction, the mode
      text appends the direction — `50% (Reverse)` or `50% (Forward)`. "Off"
      stays plain; fans with no direction attribute render unchanged.
