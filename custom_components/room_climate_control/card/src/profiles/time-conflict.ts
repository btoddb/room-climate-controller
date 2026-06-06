import type { HomeAssistant } from "../ha-types";
import { formatTimeState } from "../helpers";
import { routinesForRoom } from "./discover";
import type { RoutineConfig } from "./types";

/** Normalize to HH:MM for comparison. */
export function normalizeProfileTime(time: string): string {
  const parts = time.split(":");
  if (parts.length >= 2) {
    return `${parts[0].padStart(2, "0")}:${parts[1].padStart(2, "0")}`;
  }
  return time;
}

/** Another profile in the same room already uses this time. */
export function findTimeConflict(
  hass: HomeAssistant,
  roomKey: string,
  profileId: string,
  newTime: string
): RoutineConfig | undefined {
  const normalized = normalizeProfileTime(newTime);
  for (const r of routinesForRoom(hass, roomKey)) {
    if (r.profileId === profileId) continue;
    const existing = formatTimeState(hass.states[r.time]?.state);
    if (existing && existing === normalized) return r;
  }
  return undefined;
}

export function profileHasTimeConflict(
  hass: HomeAssistant,
  routine: RoutineConfig
): boolean {
  const t = formatTimeState(hass.states[routine.time]?.state);
  if (!t) return false;
  return Boolean(
    findTimeConflict(hass, routine.roomKey, routine.profileId, t)
  );
}

function usedTimesInRoom(hass: HomeAssistant, roomKey: string): Set<string> {
  const used = new Set<string>();
  for (const r of routinesForRoom(hass, roomKey)) {
    const t = formatTimeState(hass.states[r.time]?.state);
    if (t) used.add(normalizeProfileTime(t));
  }
  return used;
}

function minutesToHhmm(totalMins: number): string {
  const wrapped = ((totalMins % (24 * 60)) + 24 * 60) % (24 * 60);
  const h = Math.floor(wrapped / 60);
  const m = wrapped % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

/** Next 15-minute mark strictly after now; skips times already used in the room. */
export function suggestDefaultProfileTime(hass: HomeAssistant, roomKey: string): string {
  const used = usedTimesInRoom(hass, roomKey);
  const now = new Date();
  const totalMins = now.getHours() * 60 + now.getMinutes();
  let candidateMins = Math.floor(totalMins / 15) * 15 + 15;
  if (candidateMins <= totalMins) candidateMins += 15;

  for (let i = 0; i < 96; i++) {
    const candidate = minutesToHhmm(candidateMins);
    if (!used.has(candidate)) return candidate;
    candidateMins += 15;
  }
  return minutesToHhmm(candidateMins);
}

/** @deprecated Use suggestDefaultProfileTime */
export function suggestNextFreeTime(
  hass: HomeAssistant,
  roomKey: string
): string {
  return suggestDefaultProfileTime(hass, roomKey);
}
