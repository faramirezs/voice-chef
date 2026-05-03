export function formatDatetime(value: string | null | undefined) {
  if (!value) return null;
  return new Date(value).toLocaleString(
    undefined, { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}