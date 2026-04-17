export function queueRevalidateJob(tag: string): string {
  return `queued:${tag}`;
}
