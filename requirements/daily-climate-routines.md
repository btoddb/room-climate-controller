## Climate Profiles

Give the user the ability to create climate profiles (automations) per room.  Each profile has the following info set by the user:
- a name (like "before I wake up")
- a time to run
- use toggles
- Fan override toggle
- target temps

When the run time is reached, the profile (automation) is run.

The user can create as many profiles as they want.

### What they do

Each profile sets the use toggles, fan override, and the target temps for a specific room.  For instance, in Todd's bedroom there are 3 devices (cooling, heating, fan).  For each device, the profile set wheter or not to use it, and its target temp.  

If a room is in "manual mode" at the time the profile should run, the profile is ignored.

### Implementation Details

- Sunrise and Sunset automations are something different from climate control, so leave them as they are
- Set the category for a profile to **Room Profiles** (applied when profiles are synced)

## Climate Profiles UX

Instead of a new card, make a change to the existing room climate card
- Create a new section below the settings, energy use, and history buttons called, Profiles, that expands when clicking on it
  - This section header should use a bigger font to make it clear it is a new section
  - When expanded
    - You should first see a copy room button and an Add button
    - Next is the list of profiles for the room, ordered by the time they should be applied
      - Each item in the list displays the time (in AM/PM format) followed by a short name.  Make this text slightly bigger than normal text, but less than the section header
      - Each profile can be expanded by clicking it, showing the target temps, use toggles, and Fan override toggles for the room.  All are editable
        - the names of each profile should be vertically aligned and the times should be right justified in their column
- When the Add button is pressed the dialog changes, allowing the user to enter a name and a time, along with create and cancel buttons
  - The time should default to the next 15 minute interval after the current time
  - Focus should be set to the Name field
- When a profile's time occurs, the profile is applied to the room and adjustments to devices are performed based on the new values
- Create an "Apply now" button that will use the profile to immediately set the room's settings

Create copy/paste buttons for each profile.  The copy button will copy the settings for the profile to the clipboard
- When pasting:
  - Settings from the clipboard replaces the settings in the profile, but not the name and time
  - If the target profile does not support a particular target temp, the temp is ignored
  - If the target profile has a target temp that isn't on the clipboard, its value remains unchanged

### Semantic checks

- A room cannot have 2 profiles with the same time, but they can have the same name

### Implementation Details

- After pressing a button, do not inject a message into the dialog causing the text and buttons to move around or change size.  Bad UX
  - Instead, change the button to indicate success
  - Do not change the size of the button
- If the time is changed on a profile that causes the list of profiles to be reorderd, move the cursor along with the profile.  Currently the cursor will be positioned in a profile that I was not editing, but is at the same index.
- Group all scripts, helpers, blueprints, automations, etc created by the script under a category, Room Climate Control, unless it isn't possible

