import { api } from "./http";
import type {
  Game2PredictResult,
  RoundData,
  SubmitResult,
} from "../types/game";

export async function getRoundData(
  sessionId: string,
  round: number,
): Promise<RoundData> {
  return api<RoundData>(
    `/api/games/round-data?session_id=${encodeURIComponent(sessionId)}&round=${round}`,
  );
}

export async function submitGame1Answer(params: {
  session_id: string;
  round_number: number;
  user_answer: string;
  response_time_seconds: number;
  confidence: number;
}): Promise<SubmitResult> {
  return api<SubmitResult>("/api/games/answers/game1", {
    method: "POST",
    body: params,
  });
}

export async function submitGame3Answer(params: {
  session_id: string;
  round_number: number;
  selected_image_id: string;
  response_time_seconds: number;
}): Promise<SubmitResult> {
  return api<SubmitResult>("/api/games/answers/game3", {
    method: "POST",
    body: params,
  });
}

export async function predictGame2(
  formData: FormData,
): Promise<Game2PredictResult> {
  return api<Game2PredictResult>("/api/games/predict", {
    method: "POST",
    body: formData,
  });
}

export async function finalizeGame2(
  answerId: string,
  params: {
    final_answer: string;
    trust_in_ai: number;
    ai_confidence_rating: number;
  },
): Promise<SubmitResult> {
  return api<SubmitResult>(
    `/api/games/answers/${encodeURIComponent(answerId)}/finalize`,
    {
      method: "PATCH",
      body: params,
    },
  );
}