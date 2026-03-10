import { onBeforeUnmount, ref } from "vue";
import { getRoundData, predictGame2, finalizeGame2 } from "../api/games";
import { ApiError } from "../api/http";
import type {
  FourClass,
  Game2PredictResult,
  RoundData2,
  SubmitResult,
} from "../types/game";

type Step = "upload" | "result" | "final" | "done";

export function useGame2() {
  // Step tracking
  const step = ref<Step>("upload");

  // Round data
  const answerId = ref<string | null>(null);

  // Step 1 (upload + first answer)
  const selectedFile = ref<File | null>(null);
  const previewUrl = ref<string | null>(null);
  const firstAnswer = ref<FourClass | null>(null);
  const firstConfidence = ref<number | null>(null);
  const predicting = ref(false);

  // Step 2 (AI result)
  const aiResult = ref<Game2PredictResult | null>(null);

  // Step 3 (final answer)
  const finalAnswer = ref<FourClass | null>(null);
  const trustInAi = ref<number | null>(null);
  const aiConfidenceRating = ref<number | null>(null);
  const finalizing = ref(false);

  // Final result
  const submitResult = ref<SubmitResult | null>(null);

  // Common
  const loading = ref(false);
  const error = ref<string | null>(null);
  let step1StartTime: number | null = null;

  // ── Helpers ───────────────────────────────────────────────────────────────────

  function revokePreview() {
    if (previewUrl.value) {
      URL.revokeObjectURL(previewUrl.value);
      previewUrl.value = null;
    }
  }

  function setError(e: unknown) {
    error.value = e instanceof ApiError ? e.message : "Something went wrong";
  }

  // ── Actions ───────────────────────────────────────────────────────────────────

  async function loadRoundData(sessionId: string, round: number) {
    loading.value = true;
    error.value = null;
    try {
      const data = await getRoundData(sessionId, round);
      answerId.value = (data as RoundData2).answer_id;
      step.value = "upload";
      step1StartTime = Date.now();
    } catch (e) {
      setError(e);
    } finally {
      loading.value = false;
    }
  }

  function onFileSelected(file: File) {
    revokePreview();
    selectedFile.value = file;
    previewUrl.value = URL.createObjectURL(file);
    error.value = null;
  }

  async function predictAndAdvance(
    sessionId: string,
    round: number,
  ): Promise<void> {
    if (
      !selectedFile.value ||
      !firstAnswer.value ||
      firstConfidence.value == null
    )
      return;
    if (!answerId.value) return;

    const elapsed =
      step1StartTime != null ? (Date.now() - step1StartTime) / 1000 : 0;
    predicting.value = true;
    error.value = null;

    try {
      const fd = new FormData();
      fd.append("file", selectedFile.value);
      fd.append("session_id", sessionId);
      fd.append("round_number", String(round));
      fd.append("first_answer", firstAnswer.value);
      fd.append("first_confidence", String(firstConfidence.value));
      fd.append("response_time_seconds", String(elapsed));

      aiResult.value = await predictGame2(fd);
      step.value = "result";
    } catch (e) {
      setError(e);
    } finally {
      predicting.value = false;
    }
  }

  function advanceToFinalStep() {
    step.value = "final";
  }

  async function finalize(): Promise<SubmitResult | null> {
    if (
      !aiResult.value ||
      !finalAnswer.value ||
      trustInAi.value == null ||
      aiConfidenceRating.value == null
    )
      return null;

    finalizing.value = true;
    error.value = null;
    try {
      submitResult.value = await finalizeGame2(aiResult.value.answer_id, {
        final_answer: finalAnswer.value,
        trust_in_ai: trustInAi.value,
        ai_confidence_rating: aiConfidenceRating.value,
      });
      step.value = "done";
      return submitResult.value;
    } catch (e) {
      setError(e);
      return null;
    } finally {
      finalizing.value = false;
    }
  }

  function reset() {
    step.value = "upload";
    answerId.value = null;
    revokePreview();
    selectedFile.value = null;
    firstAnswer.value = null;
    firstConfidence.value = null;
    aiResult.value = null;
    finalAnswer.value = null;
    trustInAi.value = null;
    aiConfidenceRating.value = null;
    submitResult.value = null;
    error.value = null;
    step1StartTime = null;
  }

  // ── Lifecycle ──────────────────────────────────────────────────────────────────

  onBeforeUnmount(revokePreview);

  return {
    step,
    answerId,
    selectedFile,
    previewUrl,
    firstAnswer,
    firstConfidence,
    predicting,
    aiResult,
    finalAnswer,
    trustInAi,
    aiConfidenceRating,
    finalizing,
    submitResult,
    loading,
    error,
    loadRoundData,
    onFileSelected,
    predictAndAdvance,
    advanceToFinalStep,
    finalize,
    reset,
  };
}
