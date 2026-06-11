# Spec: Lovelace card & UX

The integration ships a companion Lit/TypeScript card (`custom:room-climate-control`)
and **auto-registers** it as a frontend module. The card discovers a room's
sensors, devices, and control entities from the integration; the user only picks
a room in the visual editor. Source lives in
[`card/src/`](../../custom_components/room_climate_controller/card/src/) — never
hand-edit the generated `www/` bundle.

## General UX rules

- **UX-1** Consistent styling across all cards and dialogs — buttons look and behave the same everywhere.
- **UX-2** Devices a room lacks are never shown (no empty sections).
- **UX-3** Avoid `browser_mod`. If it's the only way to implement something, ask first.
- **UX-4** Temperatures display with tenths; comparisons are whole-degree (CC-5). Show units.
- **UX-5** A fan that's **off** shows status "Off", not a 0%/speed percentage.
- **UX-6** **No layout shift on button press.** After a press, indicate success by changing the button's *appearance* (not its size) and don't inject text that reflows the dialog. Light/sound buttons briefly deactivate (~1 s) on press, then reactivate.

## Main card

- **UX-7** Centered room-name heading, larger than body text (`2.25rem`).
- **UX-8** First section: room **temperature** and **humidity** — values + units only.
- **UX-9** One section per device type the room has (Cooling / Heating / Fan), each showing:
  - **Name** — clicking opens the underlying device's more-info dialog.
  - **Target temp** (view only) and **Mode** (view only).
  - **Fan Ovr** toggle (label "Fan Ovr") — only for fan-capable heating/cooling devices; placed left of the Use toggle; editable (CC-12).
  - **Use** toggle (editable).
- **UX-10** A **Manual Mode** row aligned so its toggle lines up vertically with the Use toggles. Since manual mode has no device, it's labeled "Manual Mode" on the left.
- **UX-26** When any of the room's **window sensors** reads open (CC-20), the **Cooling** and **Heating** Use toggles are visibly disabled (dimmed, non-interactive) — their displayed state is preserved, not cleared. A status banner between the temperature/humidity row and the Cooling row always shows the window state when at least one sensor is configured: **"A window is open"** (warning color) while any window is open, **"Windows are closed"** (secondary color) when all are closed. The settings-dialog target/offset inputs, the Fan section, Fan Ovr toggles, Manual Mode, and all Profiles actions stay interactive while a window is open.
- **UX-11** Below the device sections: **Settings**, **Energy**, and **History** buttons.

## Settings dialog

- **UX-12** Shows room temp + humidity, and per device a section with **target temp**, **medium offset**, and **high offset** (target as an input field; offsets as sliders).
- **UX-13** For any device with a configured **lights & sound** command, a button that blindly sends it (per-device `*_device_button` tap_action). On press, follow UX-6 (deactivate ~1 s, then reactivate).

## Energy dialog

- **UX-14** A graph of the room's energy use (watts).

## History dialog

- **UX-15** A graph of when devices were actually **on**, plus current room temperature and outdoor temperature. "On" means the A/C/heater is actually heating/cooling — **fan-only counts as off** for this graph. No top margin.

## Graphs (Energy & History)

- **UX-16** Graphs use **lovelace-plotly-graph-card** (install via HACS) and the integration's own **graph time-range selector** (`select.*` graph_time_range, options 6/12/24/48/168 h, default 24). *(Older docs referenced an `input_select.time_range` helper; the integration now owns this selector so a fresh install works without a hand-made helper.)*
- **UX-17** Graph styling: no grid; don't fill below lines; mostly static except legend items toggle their series on/off; legend at top including current values + units; refresh interval 60 s; when the time range changes, the graph updates.
- **UX-18** Temperature axis uses a fixed 20–100 range that grows if values fall outside it. Group series sensibly to the left/right axes.

## Profiles section (on the card)

A **Profiles** section sits below the Settings/Energy/History buttons and expands
on click. See `profiles.md` for behavior.

- **UX-19** Section header uses a bigger font than body text (smaller than the room name) to mark it as a distinct section.
- **UX-20** Expanded, it shows a **Copy room** button and an **Add** button, then the room's profiles ordered by time. Each row: **time** (AM/PM, right-justified in its column) then a short **name** (vertically aligned), slightly larger than body text.
- **UX-21** Clicking a profile expands it to show editable target temps, Use toggles, and Fan-override toggles.
- **UX-22** **Add** swaps the dialog to a name + time entry with **Create**/**Cancel**. Time defaults to the next 15-minute interval; focus starts in the Name field.
- **UX-23** Each profile has **Apply now**, plus **copy/paste** buttons (PR-8–PR-10).
- **UX-24** If editing a profile's time **reorders the list**, the cursor/focus moves *with* that profile (it must not stay at the old index on a different profile).
- **UX-25** When a profile action fails (apply, rename, delete, time change, copy, paste), show a **user-readable inline error message** in that profile's row, in addition to the button's error flash. Success stays flash-only (UX-6).

## Sample dashboard

- A ready sample lives in [`examples/dashboard.yaml`](../../custom_components/room_climate_controller/examples/dashboard.yaml).
