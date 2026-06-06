import { LitElement, html, css } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import type { HomeAssistant } from "./ha-types";
import { fireConfigChanged } from "./helpers";
import { FORM_LABELS, buildFormSchema, formDataFromConfig } from "./schema";
import {
  climateRooms,
  refreshProfiles,
  subscribeProfiles,
  type ClimateRoomMeta,
} from "./profiles/store";
import type { RoomClimateUserConfig } from "./types";

@customElement("room-climate-control-editor")
export class RoomClimateControlEditor extends LitElement {
  @property({ attribute: false }) public hass!: HomeAssistant;

  @state() private _config!: RoomClimateUserConfig;
  private _unsub?: () => void;
  // Cache the schema so its reference is stable between renders (ha-form loops
  // if handed a fresh schema array each time); rebuild only when rooms change.
  private _schema?: ReturnType<typeof buildFormSchema>;
  private _schemaKey = "";

  public setConfig(config: RoomClimateUserConfig): void {
    this._config = { ...config, type: "custom:room-climate-control" };
  }

  connectedCallback(): void {
    super.connectedCallback();
    if (this.hass) void refreshProfiles(this.hass);
    this._unsub ??= subscribeProfiles(() => this.requestUpdate());
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();
    this._unsub?.();
    this._unsub = undefined;
  }

  private _getSchema(rooms: ClimateRoomMeta[]) {
    const key = rooms.map((r) => r.key).join(",");
    if (!this._schema || key !== this._schemaKey) {
      this._schema = buildFormSchema(rooms);
      this._schemaKey = key;
    }
    return this._schema;
  }

  protected render() {
    if (!this.hass || !this._config) return html``;
    const rooms = climateRooms();

    return html`
      ${rooms.length === 0
        ? html`<div class="hint">
            No Room Climate rooms found. Add a room in Settings → Devices &
            Services → Room Climate first.
          </div>`
        : html`<div class="hint">
            Pick a room; the card reads its sensors, devices, and helpers from
            the Room Climate integration automatically.
          </div>`}
      <ha-form
        .hass=${this.hass}
        .data=${formDataFromConfig(this._config)}
        .schema=${this._getSchema(rooms)}
        .computeLabel=${this._computeLabel}
        @value-changed=${this._valueChanged}
      ></ha-form>
    `;
  }

  private _computeLabel = (schema: { name: string }): string =>
    FORM_LABELS[schema.name] || schema.name;

  private _valueChanged(ev: CustomEvent): void {
    ev.stopPropagation();
    const values = ev.detail.value as Record<string, unknown>;
    const next: RoomClimateUserConfig = {
      ...this._config,
      ...values,
      type: "custom:room-climate-control",
    } as RoomClimateUserConfig;
    // Drop emptied optional fields so their defaults apply at render time.
    for (const k of ["outdoor_sensor", "time_range"] as const) {
      if (!next[k]) delete next[k];
    }
    this._config = next;
    fireConfigChanged(this, this._config);
  }

  static get styles() {
    return css`
      :host {
        display: block;
        padding: 16px;
      }
      .hint {
        margin-bottom: 12px;
        color: var(--secondary-text-color);
        font-size: 0.9em;
      }
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "room-climate-control-editor": RoomClimateControlEditor;
  }
}
