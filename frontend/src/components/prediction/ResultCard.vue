<template>
    <section class="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl shadow-black/40">
        <h2 class="text-lg font-semibold">Result</h2>

        <div class="mt-5 rounded-2xl border border-white/10 bg-black/20 p-4">
            <div v-if="!prediction" class="text-sm text-white/70">
                No prediction yet.
            </div>

            <div v-else class="space-y-2">
                <div>
                    <div class="text-xs text-white/60">Predicted label</div>
                    <div class="text-base font-semibold">
                        {{ prediction.predicted_label }}
                    </div>
                </div>

                <div>
                    <div class="mt-2 text-xs text-white/60">Confidence</div>
                    <div class="text-sm font-semibold">
                        {{ confidencePercent }}%
                    </div>
                </div>

                <div class="mt-3 h-2 w-full overflow-hidden rounded-full bg-white/10">
                    <div class="h-full rounded-full bg-[#8c0a42] transition-all"
                        :style="{ width: confidenceBarWidth }" />
                </div>

                <div class="mt-3 text-xs text-white/60">
                    Your initial marbling answer:
                    <span class="font-semibold text-white">
                        {{ prediction.student_marbling_answer }}
                    </span>
                </div>
            </div>
        </div>
    </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Prediction } from "../../api/predictions";

/* Props */

const props = defineProps<{
    prediction: Prediction | null;
}>();

/* Derived */

const confidencePercent = computed(() => {
    if (!props.prediction) return "0.00";
    return (props.prediction.confidence * 100).toFixed(2);
});

const confidenceBarWidth = computed(() => {
    if (!props.prediction) return "0%";
    const value = Math.min(
        100,
        Math.max(0, props.prediction.confidence * 100)
    );
    return `${value}%`;
});
</script>
