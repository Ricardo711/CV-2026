import { ref } from "vue";
import { getRoundData, submitGame1Answer } from "../api/games";
import { ApiError } from "../api/http";
import type { RoundData1, SubmitResult } from "../types/game";

export function useGame1() {
  const roundData = ref<RoundData1 | null>(null);
  const selectedClass = ref<string | null>(null);
  const result = ref<SubmitResult | null>(null);
  const loading = ref(false);
  const submitting = ref(false);
  const error = ref<string | null>(null);

  let startTime: number | null = null;

  // ── Actions ───────────────────────────────────────────────────────────────────

  async function loadRoundData(sessionId: string, round: number) {
    loading.value = true;
    error.value = null;
    roundData.value = null;
    selectedClass.value = null;
    result.value = null;
    try {
      const data = await getRoundData(sessionId, round);
      roundData.value = data as RoundData1;
      startTime = Date.now();
    } catch (e) {
      error.value = e instanceof ApiError ? e.message : "Error al cargar la ronda";
    } finally {
      loading.value = false;
    }
  }

  async function submit(sessionId: string, round: number): Promise<SubmitResult | null> {
    if (!roundData.value || !selectedClass.value) return null;

    const elapsed = startTime != null ? (Date.now() - startTime) / 1000 : 0;
    submitting.value = true;
    error.value = null;
    try {
      result.value = await submitGame1Answer({
        session_id: sessionId,
        round_number: round,
        user_answer: selectedClass.value,
        response_time_seconds: elapsed,
      });
      return result.value;
    } catch (e) {
      error.value = e instanceof ApiError ? e.message : "Error al enviar respuesta";
      return null;
    } finally {
      submitting.value = false;
    }
  }

  function reset() {
    roundData.value = null;
    selectedClass.value = null;
    result.value = null;
    error.value = null;
    startTime = null;
  }

  return {
    roundData,
    selectedClass,
    result,
    loading,
    submitting,
    error,
    loadRoundData,
    submit,
    reset,
  };
}
