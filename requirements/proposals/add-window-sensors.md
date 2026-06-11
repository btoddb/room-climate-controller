# Add window sensors

**Status:** proposed
**Touches:** climate-control and card-ux  *(which spec area this lands in)*

## Goal

If a room has an open window, turning on the A/C or heat is counter productive and wastes energy.  Add an option when onboarding a room to use a window sensor to prevent cooling/heating from turning on.

## Behavior

**suggestion** (open to alternatives) when it isn't obvious.

1. **constraint** If the window is open then:
   a. prevent active **cooling and heating** (Cool / Heat) from being used
   b. if cooling and/or heating is on, then turn them off
   c. UI should disable the cooling and heating **Use toggles**, preserving their state
2. **constraint** If the window is closed, then:
   a. cooling and heating can now be used again.  Each device should be evaluated by the current profile and turned on/off appropriately
   a. UI should enable the cooling and heating Use toggles
3. **constraint** If a profile is activate while window is open, it's target values should be applied, but cooling and heating cannot be used
4. **constraint** Standalone fan is not affected by the window state
5. **constraint** Manual mode always wins.  For instance, if the heater is on and the window is open, then the heater stays on
6. **constraint** **Fan-only** circulation is *not* suppressed by an open window — only active conditioning (Cool / Heat) is. This applies to the standalone fan, the fan-only override on cooling/heating devices, and a fan-capable heater's native fan-only. Fan-only moves air without spending energy heating or cooling, so it's treated like the standalone fan.
7. **constraint** A sensor reading of `unavailable` / `unknown` (or no sensor configured) is treated as **closed** — fail-safe, never suppress conditioning on bad/missing data.
8. **constraint** No debounce on window state changes (out of scope) — the controller already restarts in-flight evaluations on each change.

## UI (only if applicable)

1. **constraint** If the window is open then:
   a. UI should disable the cooling and heating **Use toggles**, preserving their displayed state, and show why (e.g. "Window open")
2. **constraint** If the window is closed, then:
   a. UI should re-enable the cooling and heating Use toggles
3. **suggestion** Profiles can still be created, deleted, and applied
4. **constraint** Only the Use toggles are disabled. The settings-dialog target/offset inputs stay editable (pre-staging a target is allowed), and the Fan-only override, Fan, and Manual Mode controls stay interactive.
5. **suggestion** Add the status of the room windows above Manual Mode in its own section.  For instance, if the Office window is open, the status would be "A window is open".  If the window is closed, the status is "windows are closed".
   a. Show the status in the same size and style as Manual Mode

## Out of scope

Multiple window sensors per room are currently out of scope.

## Acceptance criteria

How we'll know it's done — concrete checks (engine test cases, a behavior to
observe in the running app, etc.).

**Engine / unit tests:**
- [ ] `compute_commands` returns OFF for all cooling/heating devices when the window is open, regardless of temperature deltas and Use toggles
- [ ] If cooling or heating is currently on and the window opens, the engine returns commands to turn them off
- [ ] When the window closes, the engine re-evaluates each device against the currently applied targets and returns the correct on/off/speed commands — same as if the state had been freshly applied
- [ ] A standalone fan is **not** blocked by an open window (only cooling and heating are suppressed)
- [ ] Fan-only is **not** suppressed: an open window with a fan-only override (cooling/heating) or a fan-capable heater's native fan-only still runs in fan-only mode rather than off
- [ ] A profile apply while the window is open sets target values but still returns OFF for cooling/heating
- [ ] Manual mode + open window: engine skips the room entirely (manual mode wins, window state is irrelevant)

**Integration / observable behavior:**
- [ ] Opening the window in a room with active A/C turns it off within one poll/reaction cycle
- [ ] Closing the window restores devices to the state the current profile would dictate — without a manual re-apply
- [ ] If no window sensor is configured for a room, behavior is identical to today (no regression)

**Card / UI:**
- [ ] Cooling and heating **Use toggles** are visibly disabled when the window is open; their displayed state is preserved, not cleared; the row shows why ("Window open")
- [ ] Toggles re-enable when the window closes
- [ ] Settings-dialog target/offset inputs, Fan controls, Fan-only override, and Manual Mode stay interactive while the window is open
- [ ] Profile create/delete/apply actions remain available regardless of window state

**Edge cases:**
- [ ] Sensor reporting `unavailable` or `unknown` (or absent) is treated as closed (fail-safe: don't suppress heating/cooling on bad/missing sensor data)
