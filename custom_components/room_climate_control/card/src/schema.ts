/** Editor schema for the room-climate-control card.

The card discovers every device/helper entity from the integration for the
chosen room, so the editor only needs a room picker plus the two presentation
helpers the integration doesn't own (outdoor sensor + graph time-range). */
import type { ClimateRoomMeta } from "./profiles/store";

export const FORM_LABELS: Record<string, string> = {
  room: "Room",
  outdoor_sensor: "Outdoor temperature sensor (graph)",
  time_range: "Graph time-range helper",
};

export type FormFieldName = "room" | "outdoor_sensor" | "time_range";

const PRESENTATION_FIELDS = [
  {
    name: "outdoor_sensor",
    selector: {
      entity: { filter: [{ domain: "sensor", device_class: "temperature" }] },
    },
  },
  {
    name: "time_range",
    selector: { entity: { filter: [{ domain: "input_select" }] } },
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

export function formDataFromConfig(
  config: Record<string, unknown>
): Record<string, unknown> {
  return {
    room: config.room ?? "",
    outdoor_sensor: config.outdoor_sensor ?? "",
    time_range: config.time_range ?? "",
  };
}
