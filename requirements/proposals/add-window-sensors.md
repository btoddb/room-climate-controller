# Add window sensors

**Status:** in-progress
**Touches:** climate-control and card-ux  *(which spec area this lands in)*

## Goal

If a room has an open window, turning on the A/C or heat is counter productive and wastes energy.  Add an option when onboarding a room to use a window sensor to prevent cooling/heating from turning on.

## Behavior

**suggestion** (open to alternatives) when it isn't obvious.

1. **constraint** Each room can have multiple windows, and therefore multiple sensors
2. **constraint** Windows sensors only effect the cooling/heating for the room they are in
1. **constraint** If a window is open then:
   a. prevent active **cooling and heating** (Cool / Heat) from being used
   b. if cooling and/or heating are on, then turn them off
2. **constraint** If all windows are closed in a room, then:
   a. cooling and heating can now be used.  Each device should be evaluated by the active targets and turned on/off appropriately
3. **constraint** If a profile is activated while a window is open, it's target values should be applied, but cooling and heating cannot be used
4. **constraint** Standalone fan is not affected by the window state
5. **constraint** Manual mode always wins.  For instance, if the heater is on and the window is open, then the heater stays on
6. **constraint** **Fan-only** circulation is *not* suppressed by an open window — only active conditioning (Cool / Heat) is. This applies to the standalone fan, the fan-only override on cooling/heating devices, and a fan-capable heater's native fan-only. Fan-only moves air without spending energy heating or cooling, so it's treated like the standalone fan.
7. **constraint** A window sensor reading of `unavailable` / `unknown` (or no sensor configured) is treated as **closed** — fail-safe, never suppress conditioning on bad/missing data.
8. **constraint** No debounce on window state changes (out of scope) — the controller already restarts in-flight evaluations on each change.

## UI (only if applicable)

1. **constraint** If a window is open then:
   a. UI should disable the cooling and heating **Use toggles**, preserving their displayed state
2. **constraint** If a window is closed, then:
   a. UI should re-enable the cooling and heating Use toggles
3. **suggestion** Profiles can still be created, deleted, and applied
4. **constraint** Only the Use toggles are disabled. The settings-dialog target/offset inputs stay editable (pre-staging a target is allowed), and the Fan-only override, Fan, and Manual Mode controls stay interactive.
5. **suggestion** Add the status of the room windows between the temperature/humidity and Cooling, in its own section.  For instance, if an Office window is open, the status would be "A window is open".  If all windows are closed, the status is "Windows are closed".
   a. Show the status in the same size and style as Manual Mode

## Out of scope

Adding more statuses than just window status, but please prepare for more if it makes sense.

## Acceptance criteria

How we'll know it's done — concrete checks (engine test cases, a behavior to
observe in the running app, etc.).

**Engine / unit tests:**
Where it makes sense, run tests using no windows, 1 window, and 2 windows.  When there are multiple windows, test with both closed, both open, and 1 open and 1 closed

- [ ] `compute_commands` returns OFF for all cooling/heating devices when a window is open, regardless of temperature deltas and Use toggles
- [ ] If cooling or heating is currently on and a window opens, the engine returns commands to turn them off
- [ ] When all windows are closed, the engine re-evaluates each device against the currently applied targets and returns the correct on/off/speed commands — same as if the state had been freshly applied
- [ ] A standalone fan is **not** blocked by an open window (only cooling and heating are suppressed)
- [ ] Fan-only is **not** suppressed: an open window with a fan-only override (cooling/heating) or a fan-capable heater's native fan-only still runs in fan-only mode rather than off
- [ ] A profile activation or apply while a window is open sets target values but still returns OFF for cooling/heating
- [ ] Manual mode + open window: engine skips the room entirely (manual mode wins, window state is irrelevant)

**Integration / observable behavior:**
- [ ] Opening a window in a room with active A/C turns it off within one poll/reaction cycle
- [ ] Closing all the windows restores devices to the state the current profile would dictate — without a manual re-apply
- [ ] If no window sensor is configured for a room, behavior is identical to today (no regression)

**Card / UI:**
- [ ] Cooling and heating **Use toggles** are visibly disabled when a  window is open; their displayed state is preserved, not cleared; the status shows why ("A window is open")
- [ ] Toggles re-enable when all windows are closed
- [ ] Settings-dialog target/offset inputs, Fan controls, Fan-only override, and Manual Mode stay interactive while the window is open
- [ ] Profile create/delete/apply actions remain available regardless of window state

**Edge cases:**
- [ ] Sensor reporting `unavailable` or `unknown` (or absent) is treated as the window is closed (fail-safe: don't suppress heating/cooling on bad/missing sensor data)
