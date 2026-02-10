import { computed, onBeforeUnmount, reactive, ref } from "vue";
import {
  MARBLING_OPTIONS,
  type MarblingClass,
  type Prediction,
  createPrediction,
  sendFeedback,
} from "../api/predictions";
import { ApiError } from "../api/http";

// types

type FeedbackState = {
  marbling: MarblingClass | null;
  agree: number | null;
  confidence: number | null;
  helpfulness: number | null;
};

/* ---- Composable ----- */

export function usePredictionFlow() {
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
    agree: 0,
    confidence: 1,
    helpfulness: 1,
  });

  /* ---- Derived state ----- */

  const hasFile = computed(() => !!selectedFile.value);
  const hasPrediction = computed(() => !!prediction.value);

  const canPredict = computed(() => {
    return !!selectedFile.value && !!initialMarbling.value && !predicting.value;
  });

  const canSubmitFeedback = computed(() => {
    return (
      !!prediction.value &&
      !feedbackSubmitted.value &&
      !submittingFeedback.value &&
      !!feedback.value.marbling &&
      feedback.value.agree !== null &&
      feedback.value.confidence !== null &&
      feedback.value.helpfulness !== null
    );
  });

  /* UI flow helper */
  const flow = computed(() => ({
    isUpload: !hasFile.value,
    isQuestion: hasFile.value && !hasPrediction.value,
    isFeedback: hasPrediction.value,
  }));

  /* ---- Error handling ----- */

  function setError(e: unknown) {
    if (e instanceof ApiError) {
      errorMsg.value = e.message;
    } else {
      errorMsg.value = "Something went wrong. Please try again.";
    }
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
  }

  function resetAll() {
    clearError();

    selectedFile.value = null;
    revokePreview();

    initialMarbling.value = null;
    prediction.value = null;
    feedbackSubmitted.value = false;
    resetFeedback();
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

      // UX: precargar respuesta inicial
      feedback.value.marbling = initialMarbling.value;
      feedbackSubmitted.value = false;
    } catch (e) {
      setError(e);
    } finally {
      predicting.value = false;
    }
  }

  async function submitFeedback() {
    if (!prediction.value || !canSubmitFeedback.value) return;

    clearError();
    submittingFeedback.value = true;

    try {
      await sendFeedback(prediction.value.id, {
        student_marbling_answer: feedback.value.marbling as MarblingClass,
        agree_with_model: feedback.value.agree as 0 | 1,
        student_confidence: feedback.value.confidence as 1 | 2 | 3 | 4 | 5,
        helpfulness_rating: feedback.value.helpfulness as 1 | 2 | 3 | 4 | 5,
      });

      feedbackSubmitted.value = true;
    } catch (e) {
      setError(e);
    } finally {
      submittingFeedback.value = false;
    }
  }

  /* ---- Lifecycle ----- */

  onBeforeUnmount(() => {
    revokePreview();
  });

  /* ---- Public API ----- */

  return {
    // state
    selectedFile,
    previewUrl,
    initialMarbling,
    prediction,
    feedback,
    feedbackSubmitted,
    predicting,
    submittingFeedback,
    errorMsg,

    // derived
    canPredict,
    canSubmitFeedback,
    flow,

    // actions
    onFileSelected,
    onPredict,
    submitFeedback,
    resetAll,

    // constants (para componentes)
    MARBLING_OPTIONS,
  };
}
