export type ButtonFeedback = "success" | "error";

const FEEDBACK_MS = 2000;

/** Tracks temporary success/error state on action buttons. */
export class ButtonFeedbackController {
  private _feedback: Record<string, ButtonFeedback> = {};
  private _timers: Record<string, number> = {};
  private _onChange: () => void;

  constructor(onChange: () => void) {
    this._onChange = onChange;
  }

  get(key: string): ButtonFeedback | undefined {
    return this._feedback[key];
  }

  flash(key: string, result: ButtonFeedback, durationMs = FEEDBACK_MS): void {
    if (this._timers[key] !== undefined) {
      window.clearTimeout(this._timers[key]);
    }
    this._feedback = { ...this._feedback, [key]: result };
    this._onChange();
    this._timers[key] = window.setTimeout(() => {
      const next = { ...this._feedback };
      delete next[key];
      this._feedback = next;
      delete this._timers[key];
      this._onChange();
    }, durationMs);
  }

  dispose(): void {
    for (const id of Object.values(this._timers)) {
      window.clearTimeout(id);
    }
    this._timers = {};
    this._feedback = {};
  }
}
