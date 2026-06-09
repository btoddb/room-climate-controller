/** Editor schema for the room-climate-control card.

The card discovers every device/helper entity from the integration for the
chosen room, so the editor only needs a room picker and the two presentation
helpers the integration doesn't own (outdoor sensor + graph time-range). The
per-device "lights & sound" buttons are owned by the integration (configured in
the room's setup) and discovered via `rooms/list`, so they are not edited here. */
import type { ClimateRoomMeta } from "./profiles/store";

export const FORM_LABELS: Record<string, string> = {
  room: "Room",
  outdoor_sensor: "Outdoor temperature sensor",
  time_range: "Graph time-range helper",
};

export type FormFieldName = "room" | "outdoor_sensor" | "time_range";

/** Keys the editor should clear from the config when left empty. */
export const OPTIONAL_FIELDS: FormFieldName[] = ["outdoor_sensor", "time_range"];

const PRESENTATION_FIELDS = [
  {
    name: "outdoor_sensor",
    selector: {
      entity: { filter: [{ domain: "sensor", device_class: "temperature" }] },
    },
  },
  {
    name: "time_range",
    selector: { entity: { filter: [{ domain: "select" }, { domain: "input_select" }] } },
  },
] as const;

/** Build the editor schema; room options come from the integration's rooms. */
export function buildFormSchema(rooms: ClimateRoomMeta[]) {
  return [
    {
      name: "room",
      required: true,
      selector: {
        select: {
          mode: "dropdown",
          options: rooms.map((r) => ({ value: r.key, label: r.label })),
        },
      },
    },
    ...PRESENTATION_FIELDS,
  ];
}

/** Defaults discovered from the integration for the chosen room, used to
pre-fill the editor's presentation fields (e.g. the hub's outdoor sensor and
graph time-range select provided at hub setup). */
export interface DiscoveredDefaults {
  outdoor_sensor?: string | null;
  time_range?: string | null;
}

export function formDataFromConfig(
  config: Record<string, unknown>,
  defaults: DiscoveredDefaults = {}
): Record<string, unknown> {
  return {
    room: config.room ?? "",
    outdoor_sensor: config.outdoor_sensor ?? defaults.outdoor_sensor ?? "",
    time_range: config.time_range ?? defaults.time_range ?? "",
  };
}
