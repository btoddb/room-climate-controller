export interface EntityState {
  entity_id: string;
  state: string;
  attributes: Record<string, unknown>;
}

export interface HomeAssistant {
  states: Record<string, EntityState>;
  callService(
    domain: string,
    service: string,
    data?: Record<string, unknown>
  ): Promise<void>;
  /** Present on real HA frontend; used to pick up entities after helper reload. */
  callWS?<T>(message: Record<string, unknown>): Promise<T>;
  localize(key: string): string;
  formatEntityState(stateObj: EntityState): string;
}

export interface LovelaceCardConfig {
  type: string;
  [key: string]: unknown;
}

export interface LovelaceCard extends HTMLElement {
  hass?: HomeAssistant;
}

declare global {
  interface Window {
    customCards?: Array<{
      type: string;
      name: string;
      description?: string;
      preview?: boolean;
    }>;
    loadCardHelpers?: () => Promise<{
      createCardElement: (config: LovelaceCardConfig) => Promise<LovelaceCard>;
    }>;
  }

  interface HASSDomEvents {
    "hass-more-info": { entityId: string };
    "config-changed": { config: Record<string, unknown> };
  }
}

export {};
