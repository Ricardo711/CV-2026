import { api } from "./http";
import type { GameSession } from "../types/game";

export async function createSession(): Promise<GameSession> {
  return api<GameSession>("/api/sessions", { method: "POST" });
}

export async function getSession(sessionId: string): Promise<GameSession> {
  return api<GameSession>(`/api/sessions/${sessionId}`);
}
