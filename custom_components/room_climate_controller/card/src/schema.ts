/** Editor schema for the room-climate-control card.

The card discovers every device/helper entity from the integration for the
chosen room, so the editor only needs a room picker, the two presentation
helpers the integration doesn't own (outdoor sensor + graph time-range), and the
optional per-device "lights & sound" buttons. */
import type { ClimateRoomMeta } from "./profiles/store";

export const FORM_LABELS: Record<string, string> = {
  room: "Room",
  outdoor_sensor: "Outdoor temperature sensor",
  time_range: "Graph time-range helper",
  ac_device_button: "A/C lights & sound button (tap_action)",
  heater_device_button: "Heater lights & sound button (tap_action)",
  fan_device_button: "Fan lights & sound button (tap_action)",
};

export type FormFieldName =
  | "room"
  | "outdoor_sensor"
  | "time_range"
  | "ac_device_button"
  | "heater_device_button"
  | "fan_device_button";

/** Keys the editor should clear from the config when left empty. */
export const OPTIONAL_FIELDS: FormFieldName[] = [
  "outdoor_sensor",
  "time_range",
  "ac_device_button",
  "heater_device_button",
  "fan_device_button",
];

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

/** Optional per-device "lights & sound" buttons — a free-form Lovelace
tap_action object (e.g. remote.send_command). Rendered as object/YAML editors. */
const DEVICE_BUTTON_FIELDS = [
  { name: "ac_device_button", selector: { object: {} } },
  { name: "heater_device_button", selector: { object: {} } },
  { name: "fan_device_button", selector: { object: {} } },
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
    ...DEVICE_BUTTON_FIELDS,
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
    ac_device_button: config.ac_device_button,
    heater_device_button: config.heater_device_button,
    fan_device_button: config.fan_device_button,
  };
}
