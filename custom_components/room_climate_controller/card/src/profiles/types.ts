/** Shapes the profiles panel renders. Data now comes from the websocket store. */

export interface RoomPresetConfig {
  name: string;
  roomKey: string;
  has_heating?: boolean;
  has_fan?: boolean;
  useCooling?: string;
  useHeating?: string;
  useFan?: string;
  fanOverride?: string;
  fanReverse?: string;
  cooling: string;
  heating?: string;
  fan?: string;
}

export interface RoutineConfig {
  profileId: string;
  name: string;
  enabled: string;
  time: string;
  roomKey: string;
  room: RoomPresetConfig;
}
