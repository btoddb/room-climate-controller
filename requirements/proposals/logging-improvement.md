# Improve logging, again

**constraint** Don't guess, ask me questions if the proposal isn't clear

**Status:** proposed
**Touches:** climate-control | profiles

## Goal

To have a complete picture of when settings are changed, toggles are flipped, devices are commanded, etc. for troubleshooting RCC.

## Behavior

1. **constraint** (CC-L1 and CC-L6) log all sensor changes (temp, humidity, window, etc) at INFO level.  I want these logged with with a new sub-logger, "[sensor=<sensor-type>]", (like custom_components.room_climate_controller.controller or room=office) for easy filter by sensor changes.  Not sure what python calls this, but looks like a sub-logger or segment.
2. **constraint** (CC-L1) log whether or not a sensor change causes a device to be commanded, why it was commanded, (device unreachable, temp threshold, etc), and list the commands sent.  All at INFO level.
1. **constraint** (CC-L2) this shouldn't need a special case, since humidity isn't relevant to controlling **any** devices.  I want to see the sensor change, but it **must not** cause commanding a device. I still see logs like the following, which indicates it violates CC-L2:
    >2026-06-20 11:11:58.983 INFO (MainThread) [custom_components.room_climate_controller.controller] [room=office] Humidity changed: 44.43 → 44.44% (device commanded: SwitchTurnOn(entity_id='switch.office_air_conditioner_power'), SetHvacMode(entity_id='climate.office_air_conditioner', hvac_mode='fan_only'), SetTemperature(entity_id='climate.office_air_conditioner', temperature=46, hvac_mode='fan_only'), FanTurnOn(entity_id='fan.office_air_conditioner'), FanSetPreset(entity_id='fan.office_air_conditioner', preset_mode='low'))

1. **constraint** (CC-L3) I want these logged with a new sub-logger (or segment) "[profile=<profile-name>]" (like "[sensor]") for easy filtering by profile

1. **constraint** (CC-L4) I don't see logs reflecting toggles being flipped.  A message should **always** be logged at INFO level.
1. **suggestion** (CC-L4) If flipping a toggle does trigger a device command, log the commands with the toggle message at INFO level

1. **constraint** (CC-L5) Log **all** settings at INFO level for the room when adding or changing.  For remove, just log the room was removed at INFO level

1. **constraint** (CC-L7) Is this just a special case of CC-L1? Maybe on HA or RCC startup there isn't a sensor change, but devices must be commanded to enter the desired state?

1. **constraint** (CC-L8) I want these logged with a new sub-logger (like "[sensor]") called "[settings]" for easy filtering

1. **constraint** (CC-L9) this is just noise, remove it

1. **constraint** (CC-L10) I want these logged with a new sub-logger, "[capabilities]".  Log the device capabilities at INFO level using the new sub-logger

1. QUESTION: not sure what CC-L11 is trying to solve

## Acceptance criteria

[ ] new tests to ensure sensor changes effect devices accurately
[ ] specific humidity tests that ensure humidity **never** causes commanding a device

Less deterministic, but the ultimate goal is to be able to **accurately** and **clearly** trace the activity for a room, sensor, or a device