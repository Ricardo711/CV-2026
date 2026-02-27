import { api } from "./http";

export const MARBLING_OPTIONS = [
  "High Prime",
  "Average Prime",
  "Low Prime",
  "High Choice",
  "Average Choice",
  "Low Choice",
  "High Select",
  "Low Select",
  "High Standard",
] as const;

export type MarblingClass = (typeof MARBLING_OPTIONS)[number];

export type Prediction = {
  id: string;
  image_url: string;
  image_path: string;
  predicted_index: number;
  predicted_label: string;
  confidence: number;
  student_marbling_answer: string;
  created_at: string;
  feedback: null | unknown;
};

export type FeedbackPayload = {
  student_marbling_answer: MarblingClass;
  agree_with_model: 0 | 1;
  student_confidence: 1 | 2 | 3 | 4 | 5;
  helpfulness_rating: 1 | 2 | 3 | 4 | 5;
};

export async function createPrediction(params: {
  file: File;
  student_marbling_answer: MarblingClass;
}): Promise<Prediction> {
  const fd = new FormData();
  fd.append("file", params.file);
  fd.append("student_marbling_answer", params.student_marbling_answer);

  return api<Prediction>("/api/predict", { method: "POST", body: fd });
}

export async function sendFeedback(
  predictionId: string,
  payload: FeedbackPayload,
) {
  return api<any>(`/api/predictions/${predictionId}/feedback`, {
    method: "POST",
    body: payload,
  });
}

export async function sendFeedbackStep1(
  predictionId: string,
  payload: { student_marbling_answer: MarblingClass },
) {
  return api<any>(`/api/predictions/${predictionId}/feedback`, {
    method: "POST",
    body: payload,
  });
}

export async function sendFeedbackStep2(
  predictionId: string,
  payload: {
    agree_with_model: 0 | 1;
    student_confidence: 1 | 2 | 3 | 4 | 5;
    helpfulness_rating: 1 | 2 | 3 | 4 | 5;
  },
) {
  return api<any>(`/api/predictions/${predictionId}/feedback`, {
    method: "POST",
    body: payload,
  });
}
