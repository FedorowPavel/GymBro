/** Same order/labels as bot exercise_menu.MUSCLE_GROUPS */
export const MUSCLE_GROUP_ORDER = [
  "chest",
  "back",
  "biceps",
  "triceps",
  "shoulders",
  "legs",
] as const;

export type MuscleGroupId = (typeof MUSCLE_GROUP_ORDER)[number];

export const MUSCLE_GROUP_LABELS: Record<MuscleGroupId, string> = {
  chest: "Грудь",
  back: "Спина",
  biceps: "Бицепс",
  triceps: "Трицепс",
  shoulders: "Плечи",
  legs: "Ноги",
};

export function muscleGroupLabel(id: string): string {
  return MUSCLE_GROUP_LABELS[id as MuscleGroupId] ?? id;
}

export function sortMuscleGroups(ids: string[]): string[] {
  const known = new Set(MUSCLE_GROUP_ORDER);
  const ordered = MUSCLE_GROUP_ORDER.filter((id) => ids.includes(id));
  const rest = ids.filter((id) => !known.has(id as MuscleGroupId)).sort();
  return [...ordered, ...rest];
}
