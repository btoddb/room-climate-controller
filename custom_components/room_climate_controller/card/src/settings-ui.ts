import { html, nothing, type TemplateResult } from "lit";
import type { HomeAssistant } from "./ha-types";
import {
  entityConfigured,
  formatSensorValue,
  getStateObj,
  setInputNumber,
} from "./helpers";
import type { DeviceSettingsButton, RoomClimateControlConfig } from "./types";

export interface DeviceSettingsFields {
  title: string;
  target: string;
  mediumOffset: string;
  highOffset: string;
  /** When true, computed thresholds subtract offsets from target (heating). */
  subtractOffsets?: boolean;
  deviceButton?: DeviceSettingsButton;
}

function parseNum(hass: HomeAssistant, entityId: string, fallback = 0): number {
  const v = parseFloat(hass.states[entityId]?.state ?? "");
  return Number.isNaN(v) ? fallback : v;
}

function computedThreshold(
  hass: HomeAssistant,
  targetEntity: string,
  offsetEntity: string,
  subtract: boolean
): number | null {
  if (!entityConfigured(targetEntity) || !entityConfigured(offsetEntity)) return null;
  const target = parseNum(hass, targetEntity);
  const offset = parseNum(hass, offsetEntity, 1);
  return subtract ? target - offset : target + offset;
}

export function buildDeviceSettingsFields(
  config: RoomClimateControlConfig
): DeviceSettingsFields[] {
  const sections: DeviceSettingsFields[] = [];

  if (entityConfigured(config.ac_entity)) {
    sections.push({
      title: "Cooling",
      target: config.target_cooling,
      mediumOffset: config.cooling_medium_offset,
      highOffset: config.cooling_high_offset,
      deviceButton: config.ac_device_button,
    });
  }

  if (entityConfigured(config.heater_entity)) {
    sections.push({
      title: "Heating",
      target: config.target_heating,
      mediumOffset: config.heating_medium_offset,
      highOffset: config.heating_high_offset,
      subtractOffsets: true,
      deviceButton: config.heater_device_button,
    });
  }

  if (entityConfigured(config.fan_entity)) {
    sections.push({
      title: "Fan",
      target: config.target_fan,
      mediumOffset: config.fan_medium_offset,
      highOffset: config.fan_high_offset,
      deviceButton: config.fan_device_button,
    });
  }

  return sections;
}

function renderTargetRow(
  hass: HomeAssistant,
  entityId: string,
  label: string
): TemplateResult | typeof nothing {
  const obj = getStateObj(hass, entityId);
  if (!obj) return nothing;
  const min = Number(obj.attributes.min ?? 0);
  const max = Number(obj.attributes.max ?? 100);
  const step = Number(obj.attributes.step ?? 1);
  const val = parseNum(hass, entityId);

  return html`
    <div class="settings-row">
      <span class="settings-row-label">${label}</span>
      <div class="settings-row-control settings-target-control">
        <input
          type="number"
          class="settings-target-input"
          min=${min}
          max=${max}
          step=${step}
          .value=${String(val)}
          @change=${(ev: Event) => {
            const n = parseFloat((ev.target as HTMLInputElement).value);
            if (!Number.isNaN(n)) setInputNumber(hass, entityId, n);
          }}
        />
        <span class="settings-unit">°F</span>
      </div>
    </div>
  `;
}

function renderOffsetSlider(
  hass: HomeAssistant,
  entityId: string,
  label: string,
  computed: number | null
): TemplateResult | typeof nothing {
  const obj = getStateObj(hass, entityId);
  if (!obj) return nothing;
  const min = Number(obj.attributes.min ?? 1);
  const max = Number(obj.attributes.max ?? 20);
  const step = Number(obj.attributes.step ?? 1);
  const val = parseNum(hass, entityId, min);

  return html`
    <div class="settings-row">
      <div class="settings-row-label-block">
        <span class="settings-row-label">${label}</span>
        ${computed !== null
          ? html`<span class="settings-computed">→ ${computed.toFixed(0)}°F</span>`
          : nothing}
      </div>
      <div class="settings-row-control settings-slider-control">
        <input
          type="range"
          class="settings-slider"
          min=${min}
          max=${max}
          step=${step}
          .value=${String(val)}
          @input=${(ev: Event) => {
            const n = parseFloat((ev.target as HTMLInputElement).value);
            if (!Number.isNaN(n)) setInputNumber(hass, entityId, n);
          }}
        />
        <span class="settings-offset-value">${val}°F</span>
      </div>
    </div>
  `;
}

export function renderDeviceSettingsSection(
  hass: HomeAssistant,
  fields: DeviceSettingsFields,
  onDeviceButton?: (button: DeviceSettingsButton, btn: HTMLButtonElement) => void
): TemplateResult {
  const subtract = Boolean(fields.subtractOffsets);
  const medComputed = computedThreshold(
    hass,
    fields.target,
    fields.mediumOffset,
    subtract
  );
  const highComputed = computedThreshold(
    hass,
    fields.target,
    fields.highOffset,
    subtract
  );

  return html`
    <div class="settings-section">
      <div class="settings-section-title">${fields.title}</div>
      ${renderTargetRow(hass, fields.target, "Target")}
      ${renderOffsetSlider(hass, fields.mediumOffset, "Medium offset", medComputed)}
      ${renderOffsetSlider(hass, fields.highOffset, "High offset", highComputed)}
      ${fields.deviceButton && onDeviceButton
        ? html`
            <div class="settings-device-button">
              <button
                type="button"
                class="rcc-btn"
                @click=${(ev: Event) =>
                  onDeviceButton(fields.deviceButton!, ev.target as HTMLButtonElement)}
              >
                ${fields.deviceButton.name ?? "Lights & Sound"}
              </button>
            </div>
          `
        : nothing}
    </div>
  `;
}

export function renderRoomSettingsSection(
  hass: HomeAssistant,
  config: RoomClimateControlConfig
): TemplateResult | typeof nothing {
  const items: TemplateResult[] = [];

  if (entityConfigured(config.temp_sensor)) {
    items.push(html`
      <div class="settings-readout-row">
        <span class="settings-row-label">Temperature</span>
        <span class="settings-readout-value"
          >${formatSensorValue(hass, config.temp_sensor)}</span
        >
      </div>
    `);
  }

  if (entityConfigured(config.humidity_sensor)) {
    items.push(html`
      <div class="settings-readout-row">
        <span class="settings-row-label">Humidity</span>
        <span class="settings-readout-value"
          >${formatSensorValue(hass, config.humidity_sensor)}</span
        >
      </div>
    `);
  }

  if (items.length === 0) return nothing;

  return html`
    <div class="settings-section">
      <div class="settings-section-title">Room</div>
      ${items}
    </div>
  `;
}
