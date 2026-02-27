<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  currentAttempt: number;
  totalAttempts: number;
}>();

const progressPercent = computed(() =>
  Math.round(((props.currentAttempt - 1) / props.totalAttempts) * 100),
);
</script>

<template>
  <div
    class="rounded-2xl border border-white/10 bg-white/5 px-6 py-4 shadow-2xl shadow-black/40"
  >
    <div class="mb-2 flex items-center justify-between">
      <span class="text-sm font-semibold text-white/70">Progreso</span>
      <span class="text-sm font-semibold text-[#8c0a42]">
        Intento {{ currentAttempt }} de {{ totalAttempts }}
      </span>
    </div>

    <!-- Barra de progreso -->
    <div class="h-2 w-full overflow-hidden rounded-full bg-white/10">
      <div
        class="h-full rounded-full bg-[#8c0a42] transition-all duration-500"
        :style="{ width: progressPercent + '%' }"
      />
    </div>

    <!-- Segmentos indicadores -->
    <div class="mt-3 flex gap-2">
      <div
        v-for="n in totalAttempts"
        :key="n"
        class="h-2 flex-1 rounded-full transition-colors duration-300"
        :class="
          n < currentAttempt
            ? 'bg-[#8c0a42]'
            : n === currentAttempt
              ? 'bg-[#8c0a42]/50'
              : 'bg-white/10'
        "
      />
    </div>
  </div>
</template>
