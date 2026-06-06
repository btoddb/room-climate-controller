import type { HomeAssistant } from "../ha-types";
import type { RoomClimateControlConfig } from "../types";
import { buildClipboardPayload, writeRoutineClipboard } from "./clipboard";
import { buildLiveRoomFromConfig } from "./live-room";

/** Copy live room climate settings to the profile clipboard. */
export async function copyRoomSettings(
  hass: HomeAssistant,
  config: RoomClimateControlConfig,
  roomKey: string
): Promise<boolean> {
  const live = buildLiveRoomFromConfig(config, roomKey);
  if (!live) return false;
  const payload = buildClipboardPayload(hass, [live]);
  await writeRoutineClipboard(payload);
  return true;
}
