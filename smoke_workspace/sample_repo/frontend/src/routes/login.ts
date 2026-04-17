import { buildGitHubLoginUrl, handleGitHubCallback } from "../services/oauth";

export async function loginWithGitHub(): Promise<{ redirect: string }> {
  return { redirect: buildGitHubLoginUrl() };
}

export async function githubCallback(code: string): Promise<{ provider: string; code: string }> {
  return handleGitHubCallback(code);
}
