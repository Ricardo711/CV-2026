import { computed, ref } from "vue";
import { createSession } from "../api/sessions";
import { ApiError } from "../api/http";
import {
  ROUND_SEQUENCE,
  type GameSession,
  type SubmitResult,
} from "../types/game";

export function useGameSession() {
  const session = ref<GameSession | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // ── Derived ──────────────────────────────────────────────────────────────────

  const sessionId = computed(() => session.value?.id ?? null);

  const currentRound = computed(() => session.value?.current_round ?? 1);

  const isComplete = computed(() => session.value?.is_complete ?? false);

  const score = computed(() => session.value?.total_score ?? 0);

  const currentGameType = computed((): 1 | 2 | 3 => {
    const round = currentRound.value;
    return ROUND_SEQUENCE[round - 1] as 1 | 2 | 3;
  });

  // ── Actions ───────────────────────────────────────────────────────────────────

  async function startSession() {
    loading.value = true;
    error.value = null;
    try {
      session.value = await createSession();
    } catch (e) {
      error.value = e instanceof ApiError ? e.message : "Error al crear sesión";
    } finally {
      loading.value = false;
    }
  }

  /**
   * Llamado por cada componente de juego cuando la ronda termina.
   * Actualiza el estado de la sesión con el resultado del backend.
   */
  function onRoundComplete(result: SubmitResult) {
    if (!session.value) return;
    session.value.total_score = result.session_score;
    session.value.is_complete = result.is_session_complete;
    if (!result.is_session_complete) {
      session.value.current_round += 1;
    }
  }

  return {
    session,
    sessionId,
    loading,
    error,
    currentRound,
    currentGameType,
    isComplete,
    score,
    startSession,
    onRoundComplete,
  };
}
