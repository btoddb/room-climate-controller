## Overview

I want to create a new per room climate control mechanism in HA.  It will automate controlling the climate devices in the room to maintain the user's desired target temperature and humidity.  Furthermore, it should also automatically control the fan speed of each device, if there is one.  You should create and modify anything in Home Assistant to reach your goal.

## UI Style

- Style should be consistent across all cards and popup dialogs
  - For instance, buttons should all look and feel the same

## Implementation Notes

- Disregard existing configuration, helpers, dashboards, etc that might resemble a previous attempt at coding this
- Feel free to suggest additional HA extensions to make the task better, but install them using HACS
- Create a blueprint for the backend automation
- Create a sample dashboard and add a new Room Climate Control card for Todd's Bedroom, Office, and Main floor
- For a room's temperature, humidity, and power sensors, create a sensor template helper to abstract the real sensor.  This abstraction makes it easier to change sensors as my home architecture evolves, without changing blueprints, scripts, helpers, automations, etc
- If asked to create a graph, use plotly-graph and the input_select.time_range helper to define the range of the graph.
  - Be smart about grouping series to the left or right side of the graph
  - Do not show the grid
  - Do not fill below the lines
  - Make the graph fully static except allow clicking on the items in the legend, which should toggle the serious on/off 
  - For temperatures, use a fixed range from 20 to 100, and allow the range to grow if the temperatures are outside the range
  - When the time range changes, update the graph
  - Show the legend at the top and include the current values and units
  - use refresh interval = 60
- create a template sensor helper, Outdoor Temperature, that abstracts the actual entity, sensor.btoddb_weather_outdoor_temperature
- Don't use browser_mod, if at all possible.  If it's the only way to implement something, ask me before using it
- If a room does not have a device, like office doesn't have a heater, the device type should be ignored in all automations, dashboard cards, etc
- When automations trigger notifications (for instance, because of errors), send them so they appear in HA's notifications tab
  - Don't use deprecated notification methods

## Automation

### Use devices

The new mechanism should allow the user to toggle on/off the use the following devices:
- A/C device
- Heating device
- Fan device

There should be one toggle per device.  If the toggle is on, use the device to control the climate.  If the toggle is off, turn off the device unless another rule supersedes this one.

Create a user configurable target temperature for the device.  Also create a medium and high threshold offset.  When the offset is added to the target, the result defines the medium and high threshold.  The offsets range from 1 to 20.

#### Implementation Details

- For target temperature, use an input field
- For threshold offsets, use a slider on the dashboard card
- Create categories with the format Room Climate - Room Name
  - For automations, helpers, etc created for Room Climate Control assign it to the proper category
- Assign all automations, helper, etc created for Room Climate Control to the area where they are located

### Controlling A/C Device

The medium and high thresholds adhere to the following rules
- medium threshold temperature: must be > target cooling temperature, but less than the high threshold temperature
- high threshold temperature temperature: must be > medium threshold temperature
- Always set the device's target temp to its lowest value, or 65 if it can't be determined.  Since the automation controls the fan speed, the device's variable target temp isn't needed

#### Turn on/off device and set HVAC mode

- if A/C device is toggled off, power off the device
- if A/C device is toggled on
  - if room temperature > target cooling temperature, set HVAC mode = Cool and set its target temperature to its lowest possible value
  - otherwise power off the device

#### Controlling the device's fan speed, if there is one

- If the device has a fan
  - if room temperature >= high threshold temp, set fan speed = High
  - if room temperature >= medium threshold temp, but less than high threshold temp, set fan speed = Medium
  - default to set fan speed = Low

### Controlling the heating device

The medium and high thresholds adhere to the following rules
- medium threshold temperature: must be < target heating temperature, but greater than the high threshold temperature
- high threshold temperature: must be < medium threshold temperature

#### Turn on/off device and set HVAC mode

- if Heating device is toggled off, power off the device
- if Heating device is toggled on
  - if room temperature < target heating temperature, set HVAC mode = Heat and set its target temperature
  - otherwise if device has a fan, set HVAC mode = Fan Only and set its target temperature
  - otherwise power off the device

#### Controlling the device's fan, if there is one

- If the device has a fan
  - if room temperature <= high threshold temperature, set fan speed = High
  - if room temperature <= medium threshold temperature, but greater than high threshold temperature, set fan speed = Medium
  - default to set fan speed = Low

### Controlling Fan Device

The medium and high thresholds adhere to the following rules
- medium threshold temperature: must be > target fan temperature, but less than the high threshold temperature
- high threshold temperature: must be > medium threshold temperature

#### Turn on/off device

- if Fan device is toggled on and room temperature > target fan temperature
  - power on the device
- otherwise power off the device

#### Controlling the fan speed

- if room temperature >= high threshold temperature, set fan speed = High
- if room temperature >= medium threshold temperature, but less than high threshold temperature, set fan speed = Medium
- default, set fan speed = Low

#### Implementation details

- Low = 10%
- Medium = 50%
- High = 100%

### For each heating or cooling device that has a fan only mode

- Add another toggle to its settings, Use Fan Only Override
- If Fan Only Override is on
  - If use device is on, then set the device to fan only mode when the device would normally be turned off
  - If use device is off
    - If the room has a fan and its use fan toggle is on, then set the device to fan only mode
    - If the room doesn't have a fan, then set the device to fan only mode
    - otherwise set the device to off
- For devices that have both heating and cooling (like main floor heat pump), only offer Fan Only Override for Cooling

### For each device that can turn on/off its lights and/or sound

Add a button on the device's settings page that allows toggling on/off the devices lights and sound.  This might be very device specific.  I know for Todd's A/C the following tap action on a button will blindly toggle the lights and sound.

```
tap_action:
  action: perform-action
  perform_action: remote.send_command
  target:
    entity_id: remote.todd_s_bedroom_remote
  data:
    num_repeats: 1
    delay_secs: 0.4
    hold_secs: 0
    device: Todd's A/C
    command: lights
```

### Manual Mode

The user must be able to enter a "manual" mode.  This will turn off the mechanism's automation for the room, and leave the settings for each device as they are, giving the user manual control over the all devices settings.  When manual mode is turned off, the mechanism resumes control and can overwrite any settings based on its rules

### Room rules

- If the room uses the same climate device for cooling and heating, then wire the climate entity to both cooling and heating
- Figure out the target temperature range for each device and ensure the user cannot enter or select a target temperature outside of that range

#### Restrictions on settings

Target heating temperature must be less than target cooling temperature

#### When changes are made to settings

Changing a setting should trigger running any rules affected by the setting.  For instance, if the target cooling temperature is modified, all rules related to cooling devices should be run.

## Room Climate Control Dashboard card

Create a dashboard card, Room Climate Control, so the user can view relevant room sensors and control the climate for the room.  

It should have a main panel that shows the following:
- Heading with the room name, centered horizontally on the car, with a larger font than rest of text
- First section has the room's current temp and humidity
- A section for each device type: Cooling, Heating, and Fan with the following info
  - Name: clicking here shows the actual device's more info popup dialog
  - Target temp, view only
  - Mode, view only
  - if the device is heating or cooling, and it has a fan only mode, then show the Fan Only override toggle.  Name it Fan Ovr, place it to the left of the Use toggle, and it's modifiable
  - Use toggle, modifiable
  - Manual mode toggle, modifiable.  Since this mode doesn't have a device to show on the left, show "Manual Mode" instead
  - line up vertically the Use toggles with the Manual mode toggle
- Next section has settings button, energy use button, and a history button

For fan devices, when they are off, show their status as "Off", not the fan speed percentage.

### Settings ###

The settings button should popup a dialog with the following:
  - room temp and humidity
  - For each device the room has, a section with the target temp, medium threshold offset, and high threshold offset for each device
  - For each device that can toggle its lights and sound, add a button that blindly sends the command to do so.  When pressed deactivate the button for 1 second, then reactivate to show it has been pressed

### Energy Graph ###

The energy button should popup a dialog with a graph of the energy use for the room (in watts).

### History Graph ###

The history button should popup a dialog with a graph of when the devices turned on/off, current room temperature, and outdoor temperature.  It should show when the device is actually on, not just "use" turned on.

For A/C and Heaters, "on" means the A/C or Heater is turned on.  Fan only mode should be considered "off" for this graph.

### Implementation Details

#### History Graph

- no top margin on the history graph
- Dashboard card room name size = 2.25rem

