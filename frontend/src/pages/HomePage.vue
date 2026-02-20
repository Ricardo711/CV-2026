<template>
    <div class="min-h-screen bg-[#171717] text-white">
        <!-- Header -->
        <AppHeader :display-name="displayName" :email="auth.user?.email" @logout="onLogout" />

        <!-- Content -->
        <main class="mx-auto max-w-5xl px-6 py-8">
            <!-- Error -->
            <div v-if="errorMsg" class="mb-6 rounded-2xl border border-red-500/30
               bg-red-500/10 px-4 py-3 text-sm">
                {{ errorMsg }}
            </div>

            <!-- Progreso de intentos (siempre visible) -->
            <AttemptProgress
                :current-attempt="currentAttempt"
                :total-attempts="totalAttempts"
                class="mb-6"
            />

            <!-- Flujo normal: intentos 1 a 5 -->
            <div v-if="!flow.isQuiz" class="grid gap-6 lg:grid-cols-2">
                <!-- Left -->
                <section class="space-y-6">
                    <UploadCard v-if="flow.isUpload" @file-selected="onFileSelected" />

                    <MarblingQuestion v-if="flow.isQuestion" v-model="initialMarbling" :options="MARBLING_OPTIONS" />

                    <PredictActions v-if="flow.isQuestion" :can-predict="canPredict" :loading="predicting"
                        @predict="onPredict" @reset="resetAll" />

                    <FeedbackForm v-if="flow.isFeedback" v-model="feedback" :options="MARBLING_OPTIONS"
                        :prediction="prediction" :step="feedbackStep" :final-submitted="feedbackSubmitted"
                        :loading="submittingFeedback" :allow-full-reset="false"
                        @submit-step1="submitFeedbackStep1"
                        @submit-final="submitFeedbackFinal" @back="feedbackStep = 1" @reset="resetAll" />
                </section>

                <!-- Right -->
                <section class="space-y-6">
                    <ResultCard :prediction="prediction" />
                    <PreviewCard :file="selectedFile" :preview-url="previewUrl" />
                </section>
            </div>

            <!-- Pantalla de quiz: después del intento 5 -->
            <QuizScreen
                v-else
                :question="quizQuestion"
                :loading="loadingQuiz"
                @restart="resetAllAttempts"
                @retry="retryQuiz"
            />
        </main>
    </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";

import AppHeader from "../components/layout/AppHeader.vue";
import UploadCard from "../components/prediction/UploadCard.vue";
import MarblingQuestion from "../components/prediction/MarblingQuestion.vue";
import PredictActions from "../components/prediction/PredictionActions.vue";
import PreviewCard from "../components/prediction/PreviewCard.vue";
import ResultCard from "../components/prediction/ResultCard.vue";
import FeedbackForm from "../components/prediction/FeedbackForm.vue";
import AttemptProgress from "../components/quiz/AttemptProgress.vue";
import QuizScreen from "../components/quiz/QuizScreen.vue";

import { usePredictionFlow } from "../composables/usePredictionFlow";
import { useAuthStore } from "../stores/auth";

/* Auth / Router */

const auth = useAuthStore();
const router = useRouter();

/* Flow */

const {
    selectedFile,
    previewUrl,
    initialMarbling,
    prediction,
    feedback,
    feedbackSubmitted,
    predicting,
    submittingFeedback,
    errorMsg,
    canPredict,
    flow,
    onFileSelected,
    onPredict,
    resetAll,
    MARBLING_OPTIONS,
    feedbackStep,
    submitFeedbackStep1,
    submitFeedbackFinal,
    // Attempt system
    currentAttempt,
    totalAttempts,
    quizQuestion,
    loadingQuiz,
    resetAllAttempts,
    retryQuiz,
} = usePredictionFlow();

/* Computed */

const displayName = computed(() => {
    return auth.user?.full_name || auth.user?.email || "User";
});

/* Actions */

async function onLogout() {
    await auth.logout();
    router.replace({ name: "login" });
}
</script>
