import type { HomeAssistant } from "../ha-types";
import { entityConfigured } from "../helpers";
import type { RoomPresetConfig } from "./types";

export const CLIPBOARD_TYPE = "daily-routine-climate-temps" as const;

export interface ClipboardDevicePreset {
  use?: boolean;
  temp?: number;
}

export interface ClipboardRoomTemps {
  fanOverride?: boolean;
  fanReverse?: boolean;
  /** Pinned fan preset string, e.g. "sleep" or "Auto" (PR-8). */
  fanPreset?: string;
  cooling?: ClipboardDevicePreset | number;
  heating?: ClipboardDevicePreset | number;
  fan?: ClipboardDevicePreset | number;
}

export interface RoutineClipboardPayload {
  version: 1 | 2;
  type: typeof CLIPBOARD_TYPE;
  rooms: Record<string, ClipboardRoomTemps>;
}

let memoryClipboard: string | null = null;

function readTemp(hass: HomeAssistant, entityId?: string): number | undefined {
  if (!entityConfigured(entityId)) return undefined;
  const v = parseFloat(hass.states[entityId!]?.state ?? "");
  return Number.isNaN(v) ? undefined : Math.round(v);
}

function readUse(hass: HomeAssistant, entityId?: string): boolean | undefined {
  if (!entityConfigured(entityId)) return undefined;
  const s = hass.states[entityId!]?.state;
  if (s === "on") return true;
  if (s === "off") return false;
  return undefined;
}

function normalizeDevice(
  value: ClipboardDevicePreset | number | undefined
): ClipboardDevicePreset | undefined {
  if (value === undefined) return undefined;
  if (typeof value === "number") return { temp: value };
  return value;
}

export function buildClipboardPayload(
  hass: HomeAssistant,
  rooms: RoomPresetConfig[]
): RoutineClipboardPayload {
  const roomsMap: Record<string, ClipboardRoomTemps> = {};
  for (const room of rooms) {
    const entry: ClipboardRoomTemps = {};
    const coolingTemp = readTemp(hass, room.cooling);
    const coolingUse = readUse(hass, room.useCooling);
    if (coolingTemp !== undefined || coolingUse !== undefined) {
      entry.cooling = { temp: coolingTemp, use: coolingUse };
    }
    if (room.has_heating !== false) {
      const heatingTemp = readTemp(hass, room.heating);
      const heatingUse = readUse(hass, room.useHeating);
      if (heatingTemp !== undefined || heatingUse !== undefined) {
        entry.heating = { temp: heatingTemp, use: heatingUse };
      }
    }
    if (room.has_fan !== false) {
      const fanTemp = readTemp(hass, room.fan);
      const fanUse = readUse(hass, room.useFan);
      if (fanTemp !== undefined || fanUse !== undefined) {
        entry.fan = { temp: fanTemp, use: fanUse };
      }
    }
    const fanOvr = readUse(hass, room.fanOverride);
    if (fanOvr !== undefined) entry.fanOverride = fanOvr;
    const fanRev = readUse(hass, room.fanReverse);
    if (fanRev !== undefined) entry.fanReverse = fanRev;
    if (entityConfigured(room.fanPreset)) {
      const fanPresetState = hass.states[room.fanPreset!]?.state;
      if (fanPresetState) entry.fanPreset = fanPresetState;
    }

    roomsMap[room.name] = entry;
  }
  return { version: 2, type: CLIPBOARD_TYPE, rooms: roomsMap };
}

export function parseClipboardPayload(text: string): RoutineClipboardPayload | null {
  try {
    const data = JSON.parse(text) as RoutineClipboardPayload;
    if (
      (data?.version === 1 || data?.version === 2) &&
      data?.type === CLIPBOARD_TYPE &&
      data.rooms &&
      typeof data.rooms === "object"
    ) {
      return data;
    }
  } catch {
    /* invalid JSON */
  }
  return null;
}

export function applyClipboardPayload(
  hass: HomeAssistant,
  rooms: RoomPresetConfig[],
  payload: RoutineClipboardPayload,
  setValue: (entityId: string, value: number) => void,
  setUse: (entityId: string, on: boolean) => void
): number {
  let applied = 0;
  for (const room of rooms) {
    const src = payload.rooms[room.name];
    if (!src) continue;

    if (src.fanOverride !== undefined && entityConfigured(room.fanOverride)) {
      setUse(room.fanOverride!, src.fanOverride);
      applied++;
    }

    if (src.fanReverse !== undefined && entityConfigured(room.fanReverse)) {
      setUse(room.fanReverse!, src.fanReverse);
      applied++;
    }

    if (src.fanPreset !== undefined && entityConfigured(room.fanPreset)) {
      hass.callService("select", "select_option", {
        entity_id: room.fanPreset!,
        option: src.fanPreset,
      });
      applied++;
    }

    const devices: {
      key: keyof ClipboardRoomTemps;
      useId?: string;
      tempId?: string;
      enabled: boolean;
    }[] = [
      { key: "cooling", useId: room.useCooling, tempId: room.cooling, enabled: true },
      {
        key: "heating",
        useId: room.useHeating,
        tempId: room.heating,
        enabled: room.has_heating !== false,
      },
      { key: "fan", useId: room.useFan, tempId: room.fan, enabled: room.has_fan !== false },
    ];

    for (const dev of devices) {
      if (!dev.enabled) continue;
      const raw =
        dev.key === "cooling"
          ? src.cooling
          : dev.key === "heating"
            ? src.heating
            : src.fan;
      const preset = normalizeDevice(raw);
      if (!preset) continue;

      if (preset.use !== undefined && entityConfigured(dev.useId)) {
        setUse(dev.useId!, preset.use);
        applied++;
      }
      if (preset.temp !== undefined && entityConfigured(dev.tempId)) {
        setValue(dev.tempId!, preset.temp);
        applied++;
      }
    }
  }
  return applied;
}

export async function writeRoutineClipboard(payload: RoutineClipboardPayload): Promise<void> {
  const text = JSON.stringify(payload);
  memoryClipboard = text;
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      /* keep memoryClipboard */
    }
  }
}

export async function readRoutineClipboard(): Promise<string | null> {
  if (navigator.clipboard?.readText) {
    try {
      const text = await navigator.clipboard.readText();
      if (text?.trim()) {
        memoryClipboard = text;
        return text;
      }
    } catch {
      /* fall through */
    }
  }
  return memoryClipboard;
}
