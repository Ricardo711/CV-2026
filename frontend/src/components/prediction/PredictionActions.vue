<template>
    <div class="mt-6 flex flex-wrap items-center gap-3">
        <button type="button" class="rounded-xl bg-[#8c0a42] px-4 py-2 text-sm font-semibold
             hover:brightness-110 active:scale-[0.99] transition
             disabled:opacity-50 disabled:cursor-not-allowed" :disabled="!canPredict || loading"
            @click="$emit('predict')">
            <span v-if="loading">Predicting...</span>
            <span v-else>Predict</span>
        </button>

        <button type="button" class="rounded-xl border border-white/10 bg-white/5 px-4 py-2
             text-sm font-medium hover:bg-white/10
             active:scale-[0.99] transition" @click="$emit('reset')">
            Reset
        </button>
    </div>
</template>

<script setup lang="ts">
/* Props / Emits */

defineProps<{
    canPredict: boolean;
    loading: boolean;
}>();

defineEmits<{
    (e: "predict"): void;
    (e: "reset"): void;
}>();
</script>
