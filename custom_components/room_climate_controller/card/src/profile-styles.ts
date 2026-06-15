import { css } from "lit";

/** Styles for room-climate-profiles-panel (separate shadow root). */
export const profileSectionStyles = css`
  :host {
    display: block;
  }

  .rcc-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    padding: 10px 8px;
    border: none;
    border-radius: 8px;
    background: var(--secondary-background-color, rgba(0, 0, 0, 0.05));
    color: var(--primary-text-color);
    cursor: pointer;
    font: inherit;
  }

  .rcc-btn:hover:not(:disabled) {
    filter: brightness(1.04);
  }

  .rcc-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .profiles-section {
    border-top: 1px solid var(--divider-color, rgba(0, 0, 0, 0.12));
  }

  .profiles-section-summary {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 14px 16px;
    cursor: pointer;
    list-style: none;
    font-weight: 700;
    font-size: 1.4rem;
    line-height: 1.2;
  }

  .profiles-section-summary::-webkit-details-marker {
    display: none;
  }

  .profiles-count {
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--secondary-text-color);
    padding: 2px 8px;
    border-radius: 999px;
    background: var(--secondary-background-color, rgba(0, 0, 0, 0.06));
  }

  .profile-chevron {
    margin-left: auto;
    color: var(--secondary-text-color);
    transition: transform 0.15s ease;
  }

  details[open] > summary .profile-chevron {
    transform: rotate(180deg);
  }

  .profiles-section-body {
    padding: 0 16px 12px;
  }

  .profiles-toolbar {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 8px;
  }

  .profiles-loading-hint {
    font-size: 0.85rem;
    color: var(--warning-color, #ff9800);
    padding: 4px 0 8px;
  }

  .profile-add-error {
    flex: 1 1 100%;
    font-size: 0.85rem;
    color: var(--error-color, #f44336);
    padding: 4px 0;
  }

  .profile-action-btn.success {
    background: var(--success-color, #4caf50);
    color: var(--text-primary-color, #fff);
  }

  .profile-action-btn.error {
    background: var(--error-color, #f44336);
    color: var(--text-primary-color, #fff);
  }

  .profile-time-input.conflict,
  .profile-name-input.field-error {
    border-color: var(--error-color, #f44336);
  }

  .profile-time.duplicate {
    color: var(--error-color, #f44336);
  }

  .profile-item {
    border-top: 1px solid var(--divider-color, rgba(0, 0, 0, 0.08));
  }

  .profile-item-summary {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 0;
    cursor: pointer;
    list-style: none;
    font-size: 1.1rem;
    line-height: 1.25;
  }

  .profile-item-summary::-webkit-details-marker {
    display: none;
  }

  .profile-time {
    font-variant-numeric: tabular-nums;
    font-weight: 600;
    width: 5rem;
    flex-shrink: 0;
    text-align: right;
  }

  .profile-short-name {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .profile-item-body {
    padding: 0 32px 12px;
  }

  .profile-name-row {
    display: flex;
    align-items: flex-end;
    gap: 12px;
    margin-bottom: 8px;
  }

  .profile-name-field {
    display: block;
    flex: 1;
    margin-bottom: 0;
  }

  .profile-name-field .profile-name-input {
    width: 100%;
    max-width: 20rem;
    box-sizing: border-box;
  }

  .profile-schedule {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: flex-end;
    margin-bottom: 8px;
  }

  .profile-field-label {
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 0.8rem;
    color: var(--secondary-text-color);
  }

  .profile-name-input,
  .profile-time-input {
    font: inherit;
    padding: 6px 8px;
    border-radius: 6px;
    border: 1px solid var(--divider-color, rgba(0, 0, 0, 0.2));
    background: var(--card-background-color);
    color: var(--primary-text-color);
  }

  .profile-add-name {
    flex: 1;
    min-width: 140px;
  }

  .profile-add-time {
    flex-shrink: 0;
  }

  .profile-enable {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .profile-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 8px;
    justify-content: center;
  }

  .profile-action-btn {
    flex-direction: row;
    padding: 6px 10px;
    font-size: 0.85rem;
    gap: 4px;
    min-width: 6.25rem;
    box-sizing: border-box;
    justify-content: center;
  }

  .profile-action-btn > span {
    min-width: 3.25rem;
    text-align: center;
  }

  .profile-action-btn.primary {
    background: var(--primary-color);
    color: var(--text-primary-color, #fff);
  }

  .profile-action-btn.danger {
    color: var(--error-color, #f44336);
  }

  .profile-device-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 0;
  }

  .profile-device-label {
    width: 4.5rem;
    flex-shrink: 0;
    font-size: 0.9rem;
  }

  .profile-device-temp {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .profile-device-toggles {
    flex-shrink: 0;
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    gap: 8px;
  }

  .profile-use {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
  }

  .profile-use-label {
    font-size: 0.7rem;
    color: var(--secondary-text-color);
  }

  .profile-temp {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .profile-temp-input {
    width: 3.5rem;
    text-align: right;
    font: inherit;
    padding: 4px 6px;
    border-radius: 4px;
    border: 1px solid var(--divider-color, rgba(0, 0, 0, 0.2));
    background: var(--card-background-color);
    color: var(--primary-text-color);
  }

  .profile-temp-unit {
    font-size: 0.85rem;
    color: var(--secondary-text-color);
  }

  .profile-hint {
    font-size: 0.85rem;
    color: var(--secondary-text-color);
    padding: 8px 0;
  }
`;
