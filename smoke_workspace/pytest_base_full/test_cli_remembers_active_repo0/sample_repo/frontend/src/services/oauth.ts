import { queueRevalidateJob } from "../jobs/revalidate";

export function buildGitHubLoginUrl(): string {
  return "https://github.com/login/oauth/authorize";
}

export async function handleGitHubCallback(code: string): Promise<{ provider: string; code: string }> {
  queueRevalidateJob("account-settings");
  return { provider: "github", code };
}
