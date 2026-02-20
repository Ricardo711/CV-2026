import { api } from "./http";

export type QuizImage = {
  id: string;
  image_url: string;
  meat_quality_class: string;
  is_correct: boolean;
};

export type QuizQuestion = {
  target_class: string;
  images: QuizImage[];
};

export async function fetchQuizQuestion(): Promise<QuizQuestion> {
  return api<QuizQuestion>("/api/quiz/question");
}
