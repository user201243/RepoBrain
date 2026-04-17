import { handleGitHubCallback as handleCallback } from "../services/oauth";

export async function githubCallback(code: string) {
  return handleCallback(code);
}
