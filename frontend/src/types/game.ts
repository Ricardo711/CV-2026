// ── Domain constants ──────────────────────────────────────────────────────────

export const NINE_CLASSES = [
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

export const FOUR_CLASSES = ["Prime", "Choice", "Select", "Standard"] as const;

export const ROUND_SEQUENCE = [1, 3, 2, 1, 3, 2] as const;
export const TOTAL_ROUNDS = 6;

export type NineClass = (typeof NINE_CLASSES)[number];
export type FourClass = (typeof FOUR_CLASSES)[number];

// ── Session types ─────────────────────────────────────────────────────────────

export type GameSession = {
  id: string;
  student_id: string;
  start_time: string;
  end_time: string | null;
  total_score: number;
  total_rounds: number;
  current_round: number;
  is_complete: boolean;
  round_sequence: number[];
};

// ── Round data types ──────────────────────────────────────────────────────────

export type GameImageRef = {
  id: string;
  image_url: string;
};

export type RoundData1 = {
  game_type: 1;
  answer_id: string;
  image: GameImageRef;
};

export type RoundData2 = {
  game_type: 2;
  answer_id: string;
};

export type RoundData3 = {
  game_type: 3;
  answer_id: string;
  target_class: string;
  images: GameImageRef[];
};

export type RoundData = RoundData1 | RoundData2 | RoundData3;

// ── Answer types ──────────────────────────────────────────────────────────────

export type GameAnswer = {
  id: string;
  session_id: string;
  game_type: number;
  round_number: number;
  user_answer: string | null;
  correct_answer: string | null;
  is_correct: boolean | null;
  response_time_seconds: number | null;
  // Game 2 specific
  first_answer: string | null;
  first_confidence: number | null;
  ai_prediction: string | null;
  ai_confidence: number | null;
  final_answer: string | null;
  trust_in_ai: number | null;
  ai_confidence_rating: number | null;
  uploaded_image_url: string | null;
  created_at: string;
};

export type SubmitResult = {
  answer: GameAnswer;
  session_score: number;
  is_session_complete: boolean;
};

export type Game2PredictResult = {
  answer_id: string;
  ai_prediction: string;
  ai_confidence: number;
  image_url: string;
};
