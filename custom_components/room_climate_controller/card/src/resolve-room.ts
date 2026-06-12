/** Resolve a minimal user config (`room`) into a fully-populated card config by
reading the integration's room metadata from the websocket `rooms/list` cache.

This is what replaces hand-wiring every sensor/helper entity in the dashboard:
the integration is the single source of truth, the card just picks a room. */
import { getRoomsSync, roomMetaByKey } from "./profiles/store";
import type { WsRoomLive } from "./profiles/api";
import {
  DEFAULT_OUTDOOR_SENSOR,
  DEFAULT_TIME_RANGE,
  defaultConfig,
  type RoomClimateControlConfig,
  type RoomClimateUserConfig,
} from "./types";

const EMPTY_LIVE: WsRoomLive = {
  use: null,
  target: null,
  medium_offset: null,
  high_offset: null,
};

/** The room key a card points at: explicit `room`, else legacy `profile_room_key`. */
export function resolveRoomKey(user: RoomClimateUserConfig): string | undefined {
  return user.room?.trim() || user.profile_room_key?.trim() || undefined;
}

/** True once the rooms cache has been populated at least once. */
export function roomsAvailable(): boolean {
  return getRoomsSync().length > 0;
}

/** True if `key` matches a configured integration room. */
export function roomKnown(key: string): boolean {
  return getRoomsSync().some((r) => r.key === key);
}

/** Build the full render config from the chosen room's integration entities.

Returns undefined when no room key is set or the room isn't in the cache yet
(e.g. rooms/list hasn't loaded). Presentation-only fields pass through. */
export function resolveRoomConfig(
  user: RoomClimateUserConfig
): RoomClimateControlConfig | undefined {
  const key = resolveRoomKey(user);
  if (!key) return undefined;
  const room = roomMetaByKey(key);
  if (!room) return undefined;

  const e = room.entities;
  const live = (device: string): WsRoomLive => e.live[device] ?? EMPTY_LIVE;
  const cool = live("cooling");
  const heat = live("heating");
  const fan = live("fan");

  return defaultConfig({
    type: "custom:room-climate-control",
    room: key,
    profile_room_key: key,
    room_name: room.label,
    temp_sensor: e.temperature ?? "",
    humidity_sensor: e.humidity ?? "",
    power_sensor: e.power ?? "",
    ac_entity: e.ac_entity ?? "",
    heater_entity: e.heater_entity ?? "",
    fan_entity: e.fan_entity ?? "",
    window_sensors: e.window_sensors ?? [],
    manual_mode: e.manual_mode ?? "",
    ac_fan_only_override: e.ac_fan_only_override ?? "",
    heater_fan_only_override: e.heater_fan_only_override ?? "",
    fan_reversible: room.fan_reversible ?? false,
    fan_reverse_toggle: e.fan_reverse ?? "",
    use_ac: cool.use ?? "",
    target_cooling: cool.target ?? "",
    cooling_medium_offset: cool.medium_offset ?? "",
    cooling_high_offset: cool.high_offset ?? "",
    use_heater: heat.use ?? "",
    target_heating: heat.target ?? "",
    heating_medium_offset: heat.medium_offset ?? "",
    heating_high_offset: heat.high_offset ?? "",
    use_fan: fan.use ?? "",
    target_fan: fan.target ?? "",
    fan_medium_offset: fan.medium_offset ?? "",
    fan_high_offset: fan.high_offset ?? "",
    // Outdoor + time-range fall back to the integration's hub entities (the
    // outdoor mirror and the graph time-range select) before any hard default.
    outdoor_sensor: user.outdoor_sensor ?? e.outdoor ?? DEFAULT_OUTDOOR_SENSOR,
    time_range: user.time_range ?? e.time_range ?? DEFAULT_TIME_RANGE,
    // Owned by the integration (per-room device config); fall back to any
    // legacy button still set in the card's own YAML.
    ac_device_button: e.ac_device_button ?? user.ac_device_button,
    heater_device_button: e.heater_device_button ?? user.heater_device_button,
    fan_device_button: e.fan_device_button ?? user.fan_device_button,
  });
}
