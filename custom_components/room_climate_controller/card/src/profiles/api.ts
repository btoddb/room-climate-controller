/** Typed websocket client for the room_climate integration. */
import type { HomeAssistant } from "../ha-types";
import type { DeviceSettingsButton } from "../types";

export interface WsPresetDevice {
  use: boolean;
  temp: number | null;
  use_entity: string | null;
  temp_entity: string | null;
}

export interface WsProfile {
  id: string;
  name: string;
  room: string;
  icon: string;
  enabled: boolean;
  time: string | null;
  has_heating: boolean;
  has_fan: boolean;
  fan_override: boolean | null;
  fan_reverse: boolean | null;
  /** Pinned fan preset value, "Auto" when unset, null when room has no fan (PR-13). */
  fan_preset: string | null;
  entities: {
    enabled: string | null;
    time: string | null;
    fan_override: string | null;
    fan_reverse: string | null;
    /** Per-profile fan preset select entity id, null when room has no fan (PR-13). */
    fan_preset: string | null;
    presets: Record<string, WsPresetDevice>;
  };
}

export interface WsRoomLive {
  use: string | null;
  target: string | null;
  medium_offset: string | null;
  high_offset: string | null;
}

export interface WsRoom {
  key: string;
  label: string;
  area_id: string | null;
  has_ac: boolean;
  has_heating: boolean;
  has_fan: boolean;
  combined: boolean;
  /** True when the room's standalone fan supports direction via native DIRECTION feature (CC-22). */
  fan_reversible: boolean;
  entities: {
    manual_mode: string | null;
    ac_fan_only_override: string | null;
    heater_fan_only_override: string | null;
    fan_reverse: string | null;
    /** Fan preset select entity id; non-null when room has a standalone fan (CC-26). */
    fan_preset_select: string | null;
    temperature: string | null;
    humidity: string | null;
    power: string | null;
    outdoor: string | null;
    time_range: string | null;
    ac_entity: string | null;
    heater_entity: string | null;
    fan_entity: string | null;
    window_sensors: string[];
    ac_device_button: DeviceSettingsButton | null;
    heater_device_button: DeviceSettingsButton | null;
    fan_device_button: DeviceSettingsButton | null;
    live: Record<string, WsRoomLive>;
  };
}

export function wsListRooms(hass: HomeAssistant): Promise<{ rooms: WsRoom[] }> {
  return hass.callWS!({ type: "room_climate_controller/rooms/list" });
}

export function wsListProfiles(hass: HomeAssistant): Promise<{ profiles: WsProfile[] }> {
  return hass.callWS!({ type: "room_climate_controller/profiles/list" });
}

export function wsCreateProfile(
  hass: HomeAssistant,
  params: { name: string; room: string; time?: string; copy_room_settings?: boolean }
): Promise<{ profile: WsProfile }> {
  return hass.callWS!({ type: "room_climate_controller/profiles/create", ...params });
}

export function wsDeleteProfile(
  hass: HomeAssistant,
  profile_id: string
): Promise<{ success: boolean }> {
  return hass.callWS!({ type: "room_climate_controller/profiles/delete", profile_id });
}

export function wsRenameProfile(
  hass: HomeAssistant,
  profile_id: string,
  name: string
): Promise<{ profile: WsProfile }> {
  return hass.callWS!({ type: "room_climate_controller/profiles/rename", profile_id, name });
}

export function wsSetRoom(
  hass: HomeAssistant,
  profile_id: string,
  room: string
): Promise<{ success: boolean }> {
  return hass.callWS!({ type: "room_climate_controller/profiles/set_room", profile_id, room });
}

export function wsApplyProfile(
  hass: HomeAssistant,
  profile_id: string
): Promise<{ success: boolean }> {
  return hass.callWS!({ type: "room_climate_controller/profiles/apply", profile_id });
}

/** Extract a human message from a callWS rejection ({ code, message }). */
export function wsErrorMessage(err: unknown): string {
  if (err && typeof err === "object" && "message" in err) {
    const m = (err as { message?: unknown }).message;
    if (typeof m === "string") return m.trim();
  }
  return "";
}
