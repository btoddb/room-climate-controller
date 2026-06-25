import type { HomeAssistant, LovelaceCardConfig } from "./ha-types";

/** What the user actually writes in the dashboard YAML / visual editor.

The card resolves every device/helper entity from the integration's
`room_climate_controller/rooms/list` for the chosen `room`, so the only required
field is `room`. Everything else is presentation-only (not owned by the integration). */
export interface RoomClimateUserConfig extends LovelaceCardConfig {
  type: "custom:room-climate-control";
  /** Integration room key, e.g. "todd_s_bedroom". */
  room?: string;
  outdoor_sensor?: string;
  time_range?: string;
  /** Advanced/legacy: explicit room key if `room` is absent. */
  profile_room_key?: string;
}

/** Fully-resolved config the card renders from: the user's presentation fields
plus every entity discovered from the integration for the chosen room. */
export interface RoomClimateControlConfig extends LovelaceCardConfig {
  type: "custom:room-climate-control";
  /** Integration room key (new model: the card self-discovers entities). */
  room?: string;
  room_name: string;
  temp_sensor: string;
  humidity_sensor?: string;
  power_sensor?: string;
  ac_entity?: string;
  heater_entity?: string;
  fan_entity?: string;
  /** Optional window contacts; while any reads "on" (open) the engine suppresses
  cooling/heating and the card disables their Use toggles (UX-26). */
  window_sensors?: string[];
  use_ac: string;
  use_heater: string;
  use_fan: string;
  ac_fan_only_override?: string;
  heater_fan_only_override?: string;
  /** True when the standalone fan supports direction; gates the Reverse toggle (UX-28). */
  fan_reversible?: boolean;
  fan_reverse_toggle?: string;
  manual_mode: string;
  target_cooling: string;
  cooling_medium_offset: string;
  cooling_high_offset: string;
  target_heating: string;
  heating_medium_offset: string;
  heating_high_offset: string;
  target_fan: string;
  fan_medium_offset: string;
  fan_high_offset: string;
  outdoor_sensor?: string;
  time_range?: string;
  /** Room key for climate profiles (e.g. todds_bedroom). Inferred from manual_mode if omitted. */
  profile_room_key?: string;
}

export type DialogType = "settings" | "energy" | "history" | null;

export const DEFAULT_OUTDOOR_SENSOR = "sensor.outdoor_temperature";
// The integration owns the time-range select and the card discovers its entity
// id from rooms/list, so there is no hard default to fall back to.
export const DEFAULT_TIME_RANGE = "";

export function defaultConfig(
  partial: Partial<RoomClimateControlConfig> = {}
): RoomClimateControlConfig {
  return {
    type: "custom:room-climate-control",
    room_name: "Room",
    temp_sensor: "",
    use_ac: "",
    use_heater: "",
    use_fan: "",
    manual_mode: "",
    target_cooling: "",
    cooling_medium_offset: "",
    cooling_high_offset: "",
    target_heating: "",
    heating_medium_offset: "",
    heating_high_offset: "",
    target_fan: "",
    fan_medium_offset: "",
    fan_high_offset: "",
    outdoor_sensor: DEFAULT_OUTDOOR_SENSOR,
    time_range: DEFAULT_TIME_RANGE,
    ...partial,
  };
}
