import { computed, onBeforeUnmount, ref } from "vue";
import {
  MARBLING_OPTIONS,
  type MarblingClass,
  type Prediction,
  createPrediction,
  sendFeedbackStep1,
  sendFeedbackStep2,
} from "../api/predictions";
import { ApiError } from "../api/http";
import { fetchQuizQuestion, type QuizQuestion } from "../api/quiz";

// types
type FeedbackState = {
  marbling: MarblingClass | null;
  agree: number | null; // 0|1
  confidence: number | null; // 1..5
  helpfulness: number | null; // 1..5
};

const TOTAL_ATTEMPTS = 5;

export function usePredictionFlow() {
  /* ---------- Attempt-level state ---------- */

  const currentAttempt = ref(1);
  const allAttemptsComplete = ref(false);
  const quizQuestion = ref<QuizQuestion | null>(null);
  const loadingQuiz = ref(false);
  let advanceTimer: ReturnType<typeof setTimeout> | null = null;

  /* ---------- Core state ---------- */

  const selectedFile = ref<File | null>(null);
  const previewUrl = ref<string | null>(null);

  const initialMarbling = ref<MarblingClass | null>(null);
  const prediction = ref<Prediction | null>(null);

  const predicting = ref(false);
  const submittingFeedback = ref(false);

  const feedbackSubmitted = ref(false);
  const errorMsg = ref<string | null>(null);

  /* ---------- Feedback ---------- */

  const feedback = ref<FeedbackState>({
    marbling: null,
    agree: null,
    confidence: null,
    helpfulness: null,
  });

  const feedbackStep = ref<1 | 2>(1);

  /* ---- Derived state ----- */

  const hasFile = computed(() => !!selectedFile.value);
  const hasPrediction = computed(() => !!prediction.value);

  const canPredict = computed(() => {
    return !!selectedFile.value && !!initialMarbling.value && !predicting.value;
  });

  // Validaciones por paso
  const canSubmitFeedbackStep1 = computed(() => {
    return (
      !!prediction.value &&
      !feedbackSubmitted.value &&
      !submittingFeedback.value &&
      !!feedback.value.marbling
    );
  });

  const canSubmitFeedbackFinal = computed(() => {
    return (
      !!prediction.value &&
      !feedbackSubmitted.value &&
      !submittingFeedback.value &&
      feedback.value.agree !== null &&
      feedback.value.confidence !== null &&
      feedback.value.helpfulness !== null
    );
  });

  /* UI flow helper - incluye isQuiz para la pantalla final */
  const flow = computed(() => ({
    isUpload: !allAttemptsComplete.value && !hasFile.value,
    isQuestion: !allAttemptsComplete.value && hasFile.value && !hasPrediction.value,
    isFeedback: !allAttemptsComplete.value && hasPrediction.value,
    isQuiz: allAttemptsComplete.value,
  }));

  /* ---- Error handling ----- */

  function setError(e: unknown) {
    if (e instanceof ApiError) errorMsg.value = e.message;
    else errorMsg.value = "Something went wrong. Please try again.";
  }

  function clearError() {
    errorMsg.value = null;
  }

  /* ---- Helpers ----- */

  function revokePreview() {
    if (previewUrl.value) {
      URL.revokeObjectURL(previewUrl.value);
      previewUrl.value = null;
    }
  }

  function resetFeedback() {
    feedback.value.marbling = null;
    feedback.value.agree = null;
    feedback.value.confidence = null;
    feedback.value.helpfulness = null;
  }

  /* ---- Quiz helpers ----- */

  async function _loadQuizQuestion() {
    loadingQuiz.value = true;
    quizQuestion.value = null;
    clearError();
    try {
      quizQuestion.value = await fetchQuizQuestion();
    } catch (e) {
      setError(e);
    } finally {
      loadingQuiz.value = false;
    }
  }

  /** Avanza al siguiente intento: incrementa contador y limpia estado de intento actual */
  function _advanceToNextAttempt() {
    currentAttempt.value += 1;
    // Limpiar estado del intento (NO tocar currentAttempt ni allAttemptsComplete)
    selectedFile.value = null;
    revokePreview();
    initialMarbling.value = null;
    prediction.value = null;
    feedbackSubmitted.value = false;
    resetFeedback();
    feedbackStep.value = 1;
    clearError();
  }

  /* ---- Actions ----- */

  function onFileSelected(file: File) {
    clearError();
    revokePreview();

    selectedFile.value = file;
    previewUrl.value = URL.createObjectURL(file);

    initialMarbling.value = null;
    prediction.value = null;
    feedbackSubmitted.value = false;

    resetFeedback();
    feedbackStep.value = 1;
  }

  /** Reinicia solo el intento actual (no retrocede el contador de intentos) */
  function resetAll() {
    clearError();

    selectedFile.value = null;
    revokePreview();

    initialMarbling.value = null;
    prediction.value = null;
    feedbackSubmitted.value = false;

    resetFeedback();
    feedbackStep.value = 1;
  }

  /** Reinicia completamente la sesión (5 intentos desde cero) */
  function resetAllAttempts() {
    if (advanceTimer) clearTimeout(advanceTimer);
    currentAttempt.value = 1;
    allAttemptsComplete.value = false;
    quizQuestion.value = null;
    resetAll();
  }

  async function onPredict() {
    if (!selectedFile.value || !initialMarbling.value) return;

    clearError();
    predicting.value = true;

    try {
      const res = await createPrediction({
        file: selectedFile.value,
        student_marbling_answer: initialMarbling.value,
      });

      prediction.value = res;

      // UX: precargar marbling en feedback
      feedback.value.marbling = initialMarbling.value;
      feedbackSubmitted.value = false;
      feedbackStep.value = 1;
    } catch (e) {
      setError(e);
    } finally {
      predicting.value = false;
    }
  }

  // enviar solo Q1 y avanzar
  async function submitFeedbackStep1() {
    if (!prediction.value || !canSubmitFeedbackStep1.value) return;

    clearError();
    submittingFeedback.value = true;

    try {
      await sendFeedbackStep1(prediction.value.id, {
        student_marbling_answer: feedback.value.marbling as MarblingClass,
      });

      feedbackStep.value = 2;
    } catch (e) {
      setError(e);
    } finally {
      submittingFeedback.value = false;
    }
  }

  // enviar Q2-Q4 y marcar como submitted; si es el último intento → quiz
  async function submitFeedbackFinal() {
    if (!prediction.value || !canSubmitFeedbackFinal.value) return;

    clearError();
    submittingFeedback.value = true;

    try {
      await sendFeedbackStep2(prediction.value.id, {
        agree_with_model: feedback.value.agree as 0 | 1,
        student_confidence: feedback.value.confidence as 1 | 2 | 3 | 4 | 5,
        helpfulness_rating: feedback.value.helpfulness as 1 | 2 | 3 | 4 | 5,
      });

      feedbackSubmitted.value = true;

      if (currentAttempt.value >= TOTAL_ATTEMPTS) {
        // Último intento completado → cargar quiz
        allAttemptsComplete.value = true;
        await _loadQuizQuestion();
      } else {
        // Avanzar al siguiente intento después de un breve delay
        // para que el estudiante vea el badge "Submitted"
        advanceTimer = setTimeout(() => {
          _advanceToNextAttempt();
        }, 1200);
      }
    } catch (e) {
      setError(e);
    } finally {
      submittingFeedback.value = false;
    }
  }

  function goBackToStep1() {
    if (feedbackSubmitted.value) return;
    feedbackStep.value = 1;
  }

  /* ---- Lifecycle ----- */

  onBeforeUnmount(() => {
    revokePreview();
    if (advanceTimer) clearTimeout(advanceTimer);
  });

  /* ---- Public API ----- */

  return {
    // state
    selectedFile,
    previewUrl,
    initialMarbling,
    prediction,
    feedback,
    feedbackStep,
    feedbackSubmitted,
    predicting,
    submittingFeedback,
    errorMsg,

    // attempt state
    currentAttempt,
    totalAttempts: TOTAL_ATTEMPTS,
    allAttemptsComplete,
    quizQuestion,
    loadingQuiz,

    // derived
    canPredict,
    canSubmitFeedbackStep1,
    canSubmitFeedbackFinal,
    flow,

    // actions
    onFileSelected,
    onPredict,
    submitFeedbackStep1,
    submitFeedbackFinal,
    goBackToStep1,
    resetAll,
    resetAllAttempts,
    retryQuiz: _loadQuizQuestion,

    // constants
    MARBLING_OPTIONS,
  };
}
