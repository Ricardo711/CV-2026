<script setup lang="ts">
import { ref, computed } from "vue";
import type { QuizQuestion, QuizImage } from "../../api/quiz";

const props = defineProps<{
  question: QuizQuestion | null;
  loading: boolean;
}>();

const emit = defineEmits<{
  (e: "restart"): void;
  (e: "retry"): void;
}>();

const selectedId = ref<string | null>(null);
const answered = ref(false);

const selectedImage = computed<QuizImage | null>(() => {
  if (!selectedId.value || !props.question) return null;
  return props.question.images.find((img) => img.id === selectedId.value) ?? null;
});

const isCorrect = computed(() => selectedImage.value?.is_correct ?? false);

function selectImage(img: QuizImage) {
  if (answered.value) return;
  selectedId.value = img.id;
  answered.value = true;
}

function imageCardClass(img: QuizImage): string {
  if (!answered.value) {
    if (selectedId.value === img.id) {
      return "border-[#8c0a42] bg-[#8c0a42]/10";
    }
    return "border-white/10 bg-black/20 hover:border-[#8c0a42]/50 hover:bg-[#8c0a42]/5 cursor-pointer";
  }
  // Después de responder: revelar
  if (img.is_correct) {
    return "border-emerald-400 bg-emerald-500/10";
  }
  if (img.id === selectedId.value) {
    return "border-red-500 bg-red-500/10";
  }
  return "border-white/5 bg-black/20 opacity-50";
}
</script>

<template>
  <div class="space-y-6">
    <!-- Estado: cargando -->
    <div
      v-if="loading"
      class="rounded-2xl border border-white/10 bg-white/5 p-10 shadow-2xl shadow-black/40"
    >
      <div class="flex flex-col items-center gap-4 text-white/50">
        <div
          class="h-8 w-8 animate-spin rounded-full border-2 border-white/20 border-t-[#8c0a42]"
        />
        <p class="text-sm font-medium">Loading quiz...</p>
      </div>
    </div>

    <!-- Estado: error (sin question) -->
    <div
      v-else-if="!question"
      class="rounded-2xl border border-white/10 bg-white/5 p-10 shadow-2xl shadow-black/40"
    >
      <div class="flex flex-col items-center gap-4 text-center">
        <p class="text-sm text-white/50">Could not load quiz question.</p>
        <button
          class="rounded-full border border-white/10 bg-white/5 px-5 py-2 text-sm font-medium text-white/70 transition hover:bg-white/10 active:scale-[0.99]"
          @click="emit('retry')"
        >
          Try again
        </button>
      </div>
    </div>

    <!-- Quiz activo -->
    <template v-else>
      <!-- Tarjeta de pregunta -->
      <div
        class="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl shadow-black/40"
      >
        <p class="text-center text-base font-semibold leading-relaxed text-white/90">
          Could you identify the marbling quality of the
          <span class="text-[#8c0a42]">{{ question.target_class }}</span> class?
        </p>
      </div>

      <!-- Grid de 3 imágenes -->
      <div class="grid grid-cols-3 gap-4">
        <button
          v-for="img in question.images"
          :key="img.id"
          class="group rounded-2xl border-2 p-2 shadow-xl shadow-black/30 transition-all duration-200"
          :class="imageCardClass(img)"
          :disabled="answered"
          @click="selectImage(img)"
        >
          <!-- Imagen real -->
          <div
            v-if="img.image_url"
            class="aspect-square w-full overflow-hidden rounded-xl"
          >
            <img
              :src="img.image_url"
              :alt="img.meat_quality_class"
              class="h-full w-full object-cover"
            />
          </div>

          <!-- Placeholder cuando no hay imagen -->
          <div
            v-else
            class="aspect-square w-full overflow-hidden rounded-xl bg-white/5"
          >
            <div class="flex h-full flex-col items-center justify-center gap-2 p-3">
              <span class="text-3xl text-white/20">?</span>
              <span class="text-center text-xs font-semibold leading-tight text-white/40">
                {{ img.meat_quality_class }}
              </span>
            </div>
          </div>

          <!-- Indicador de resultado bajo la imagen -->
          <div v-if="answered" class="mt-2 text-center">
            <span
              v-if="img.is_correct"
              class="text-xs font-semibold text-emerald-300"
            >✓ Correct</span>
            <span
              v-else-if="img.id === selectedId"
              class="text-xs font-semibold text-red-400"
            >✗ Wrong</span>
          </div>
        </button>
      </div>

      <!-- Feedback de resultado -->
      <div
        v-if="answered"
        class="rounded-2xl border p-5 shadow-2xl shadow-black/40 transition-all"
        :class="
          isCorrect
            ? 'border-emerald-400/40 bg-emerald-500/10'
            : 'border-red-500/40 bg-red-500/10'
        "
      >
        <p
          class="text-center text-sm font-semibold"
          :class="isCorrect ? 'text-emerald-300' : 'text-red-300'"
        >
          {{
            isCorrect
              ? "Correct! You identified the marbling quality accurately."
              : `Not quite. The correct answer was "${question.target_class}".`
          }}
        </p>
      </div>

      <!-- Botón Play Again (visible después de responder) -->
      <div v-if="answered" class="flex justify-center pt-2">
        <button
          class="rounded-full bg-[#8c0a42] px-8 py-3 text-sm font-semibold text-white shadow-lg transition hover:brightness-110 active:scale-[0.99]"
          @click="emit('restart')"
        >
          Play Again
        </button>
      </div>
    </template>
  </div>
</template>
