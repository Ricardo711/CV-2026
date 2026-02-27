<template>
    <section class="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl shadow-black/40">
        <!-- Header -->
        <div class="flex items-start justify-between gap-4">
            <div>
                <h2 class="text-lg font-semibold">Feedback</h2>
                <p class="mt-1 text-sm text-white/70">
                    Step {{ step }} of 2
                </p>
            </div>

            <div v-if="finalSubmitted"
                class="rounded-xl bg-emerald-500/15 px-3 py-1 text-xs font-semibold text-emerald-200">
                Submitted
            </div>
        </div>

        <!-- STEP 1 -->
        <div v-if="step === 1" class="mt-5">
            <div class="text-sm font-semibold">
                1. What marbling class belongs to your image?
            </div>

            <div class="mt-3 grid gap-2 sm:grid-cols-2">
                <label v-for="opt in options" :key="opt" class="flex cursor-pointer items-center gap-2 rounded-xl
                 border border-white/10 bg-black/20 px-3 py-2
                 hover:border-[#8c0a42]/50 hover:bg-[#8c0a42]/10 transition">
                    <input class="h-4 w-4 accent-[#8c0a42]" type="radio" name="feedback-marbling" :value="opt"
                        :checked="modelValue.marbling === opt" @change="update('marbling', opt)" />
                    <span class="text-sm">{{ opt }}</span>
                </label>
            </div>

            <!-- Actions step 1 -->
            <div class="mt-6 flex flex-wrap items-center gap-3">
                <button type="button" class="rounded-xl bg-[#8c0a42] px-4 py-2 text-sm font-semibold hover:brightness-110
                 active:scale-[0.99] transition disabled:opacity-50 disabled:cursor-not-allowed"
                    :disabled="!canSubmitStep1 || loading" @click="$emit('submit-step1')">
                    <span v-if="loading">Saving...</span>
                    <span v-else>Next</span>
                </button>

                <button v-if="allowFullReset !== false" type="button" class="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium
                 hover:bg-white/10 active:scale-[0.99] transition" @click="$emit('reset')">
                    New prediction
                </button>
            </div>
        </div>

        <!-- STEP 2 -->
        <div v-else class="mt-5">
            <!-- Q2 -->
            <div>
                <div class="text-sm font-semibold">
                    2. Do you agree with the AI prediction?
                </div>

                <div class="mt-3 flex gap-3">
                    <label v-for="opt in agreeOptions" :key="opt.value" class="flex cursor-pointer items-center gap-2 rounded-xl
                   border border-white/10 bg-black/20 px-3 py-2
                   hover:border-[#8c0a42]/50 hover:bg-[#8c0a42]/10 transition">
                        <input class="h-4 w-4 accent-[#8c0a42]" type="radio" name="feedback-agree" :value="opt.value"
                            :checked="modelValue.agree === opt.value" @change="update('agree', opt.value)" />
                        <span class="text-sm">{{ opt.label }}</span>
                    </label>
                </div>
            </div>

            <!-- Q3 -->
            <div class="mt-6">
                <div class="text-sm font-semibold">
                    3. How confident are you in your final answer?
                </div>

                <div class="mt-3 flex flex-wrap gap-2">
                    <button v-for="n in scale" :key="'conf-' + n" type="button"
                        class="rounded-xl border px-3 py-2 text-sm font-semibold transition"
                        :class="scaleClass(modelValue.confidence === n)" @click="update('confidence', n)">
                        {{ n }}
                    </button>
                </div>
            </div>

            <!-- Q4 -->
            <div class="mt-6">
                <div class="text-sm font-semibold">
                    4. How helpful was the AI for this image?
                </div>

                <div class="mt-3 flex flex-wrap gap-2">
                    <button v-for="n in scale" :key="'help-' + n" type="button"
                        class="rounded-xl border px-3 py-2 text-sm font-semibold transition"
                        :class="scaleClass(modelValue.helpfulness === n)" @click="update('helpfulness', n)">
                        {{ n }}
                    </button>
                </div>
            </div>

            <!-- Actions step 2 -->
            <div class="mt-6 flex flex-wrap items-center gap-3">
                <div v-if="!finalSubmitted" class="flex flex-wrap items-center gap-3">
                    <button type="button" class="rounded-xl bg-[#8c0a42] px-4 py-2 text-sm font-semibold hover:brightness-110
                     active:scale-[0.99] transition disabled:opacity-50 disabled:cursor-not-allowed"
                        :disabled="!canSubmitStep2 || loading" @click="$emit('submit-final')">
                        <span v-if="loading">Submitting...</span>
                        <span v-else>Submit feedback</span>
                    </button>
    
                    <button type="button" class="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium
                     hover:bg-white/10 active:scale-[0.99] transition" @click="$emit('back')"
                        :disabled="loading || finalSubmitted">
                        Back
                    </button>
                </div>

                <button v-if="allowFullReset !== false" type="button" class="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium
                 hover:bg-white/10 active:scale-[0.99] transition" @click="$emit('reset')">
                    New prediction
                </button>
            </div>
        </div>
    </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { MarblingClass, Prediction } from "../../api/predictions";

type FeedbackModel = {
    marbling: string | null;
    agree: number | null;
    confidence: number | null;
    helpfulness: number | null;
};

const props = defineProps<{
    modelValue: FeedbackModel;
    options: readonly MarblingClass[];
    prediction: Prediction | null;
    step: 1 | 2;
    finalSubmitted: boolean;
    loading: boolean;
    allowFullReset?: boolean;
}>();

const emit = defineEmits<{
    (e: "update:modelValue", value: FeedbackModel): void;
    (e: "submit-step1"): void;
    (e: "submit-final"): void;
    (e: "back"): void;
    (e: "reset"): void;
}>();

const agreeOptions = [
    { label: "Yes", value: 1 as const },
    { label: "No", value: 0 as const },
];

const scale = [1, 2, 3, 4, 5] as const;

const canSubmitStep1 = computed(() => !!props.modelValue.marbling && !!props.prediction);
const canSubmitStep2 = computed(() => {
    return (
        !!props.prediction &&
        props.modelValue.agree !== null &&
        props.modelValue.confidence !== null &&
        props.modelValue.helpfulness !== null
    );
});

function update<K extends keyof FeedbackModel>(key: K, value: FeedbackModel[K]) {
    emit("update:modelValue", { ...props.modelValue, [key]: value });
}

function scaleClass(active: boolean) {
    return active
        ? "border-[#8c0a42] bg-[#8c0a42]/20 text-white"
        : "border-white/10 bg-black/20 text-white/80 hover:border-[#8c0a42]/50 hover:bg-[#8c0a42]/10";
}
</script>
