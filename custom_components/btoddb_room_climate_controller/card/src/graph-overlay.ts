const STYLE_ID = "room-climate-overlay-styles";

const OVERLAY_CSS = `
  .rcc-overlay {
    position: fixed;
    inset: 0;
    z-index: 2000;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.5);
    padding: 16px;
  }

  .rcc-overlay-panel {
    background: var(--card-background-color, #fff);
    color: var(--primary-text-color, #212121);
    border-radius: 12px;
    width: min(920px, 95vw);
    max-height: 90vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
  }

  .rcc-overlay-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px 8px;
    font-size: 1.25rem;
    font-weight: 500;
  }

  .rcc-overlay-close {
    border: none;
    background: transparent;
    cursor: pointer;
    color: inherit;
    padding: 4px;
    border-radius: 50%;
    display: flex;
  }

  .rcc-overlay-close:hover {
    background: var(--secondary-background-color, rgba(0, 0, 0, 0.08));
  }

  .rcc-overlay-body {
    padding: 0 16px 16px;
    overflow-y: auto;
    max-height: calc(90vh - 56px);
  }

  .rcc-overlay-graph-host {
    min-height: 400px;
  }

  .rcc-overlay-power-now {
    padding: 8px 16px;
    color: var(--secondary-text-color, #666);
  }
`;

export function ensureOverlayStyles(): void {
  if (document.getElementById(STYLE_ID)) return;
  const style = document.createElement("style");
  style.id = STYLE_ID;
  style.textContent = OVERLAY_CSS;
  document.head.appendChild(style);
}

export class GraphOverlay {
  private root?: HTMLElement;
  private body?: HTMLElement;
  private onClose?: () => void;

  get isOpen(): boolean {
    return Boolean(this.root);
  }

  open(title: string, onClose: () => void): HTMLElement {
    this._removeDom();
    ensureOverlayStyles();
    this.onClose = onClose;

    this.root = document.createElement("div");
    this.root.className = "rcc-overlay";
    this.root.addEventListener("click", (ev) => {
      if (ev.target === this.root) this.close();
    });

    const panel = document.createElement("div");
    panel.className = "rcc-overlay-panel";

    const header = document.createElement("div");
    header.className = "rcc-overlay-header";
    header.textContent = title;

    const closeBtn = document.createElement("button");
    closeBtn.className = "rcc-overlay-close";
    closeBtn.setAttribute("aria-label", "Close");
    closeBtn.innerHTML = '<ha-icon icon="mdi:close"></ha-icon>';
    closeBtn.addEventListener("click", () => this.close());
    header.appendChild(closeBtn);

    this.body = document.createElement("div");
    this.body.className = "rcc-overlay-body";

    panel.appendChild(header);
    panel.appendChild(this.body);
    this.root.appendChild(panel);
    document.body.appendChild(this.root);

    return this.body;
  }

  close(): void {
    this._removeDom();
    const cb = this.onClose;
    this.onClose = undefined;
    cb?.();
  }

  /** Remove overlay DOM without notifying close (used when remounting content). */
  private _removeDom(): void {
    if (this.root) {
      this.root.remove();
      this.root = undefined;
      this.body = undefined;
    }
  }
}
