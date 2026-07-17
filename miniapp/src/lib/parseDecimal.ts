/** Parses a decimal number from user input, accepting comma or dot as separator. */
export function parseDecimalInput(value: string): number | null {
  const trimmed = value.trim();
  if (trimmed === "") {
    return null;
  }
  const normalized = trimmed.replace(",", ".");
  const n = Number(normalized);
  return Number.isFinite(n) ? n : null;
}
