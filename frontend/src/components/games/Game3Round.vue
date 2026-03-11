<template>
    <div class="space-y-4">
        <!-- Loading -->
        <div v-if="game3.loading.value" class="flex items-center justify-center py-16">
            <div class="text-sm text-white/60">Loading images…</div>
        </div>

        <!-- Error -->
        <div
            v-else-if="game3.error.value"
            class="rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400"
        >
            {{ game3.error.value }}
        </div>

        <template v-else-if="game3.roundData.value">
            <section class="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl shadow-black/40">
                <h2 class="text-lg font-semibold text-white">Image Selection</h2>
                <p class="my-1 text-sm text-white/70">
                    Select the image that corresponds to
                    <span class="font-bold text-[#e0608a]">
                        {{ game3.roundData.value.target_class }}
                    </span>.
                </p>

                <div class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-3">
                    <button
                        v-for="img in game3.roundData.value.images"
                        :key="img.id"
                        type="button"
                        class="relative overflow-hidden rounded-2xl border-2 transition aspect-square"
                        :class="getImageCardClass(img.id)"
                        @click="handleSelect(img.id)"
                    >
                        <div
                            v-if="game3.result.value && getImageState(img.id) === 'correct'"
                            class="absolute left-3 top-3 z-10 rounded-full border border-green-500/30 bg-green-500/20 px-3 py-1 text-xs font-bold text-green-400"
                        >
                            Correct!
                        </div>

                        <div
                            v-else-if="game3.result.value && getImageState(img.id) === 'wrong'"
                            class="absolute left-3 top-3 z-10 rounded-full border border-red-500/30 bg-red-500/20 px-3 py-1 text-xs font-bold text-red-400"
                        >
                            Incorrect!
                        </div>

                        <img
                            v-if="img.image_url"
                            :src="img.image_url"
                            alt="Meat image option"
                            class="h-full w-full object-cover"
                        />
                        <div v-else class="grid h-full place-items-center p-4">
                            <div class="text-3xl opacity-30">🥩</div>
                        </div>
                    </button>
                </div>

                <div v-if="game3.result.value" class="mt-6">
                    <div class="flex items-center gap-3">
                        <div
                            class="rounded-full border px-4 py-1 text-sm font-bold"
                            :class="
                                game3.result.value.answer.is_correct
                                    ? 'border-green-500/30 bg-green-500/20 text-green-400'
                                    : 'border-red-500/30 bg-red-500/20 text-red-400'
                            "
                        >
                            {{ game3.result.value.answer.is_correct ? "Correct!" : "Incorrect!" }}
                        </div>
                    </div>

                    <p class="mt-3 text-sm text-white/70">
                        <template v-if="game3.result.value.answer.is_correct">
                            You selected the correct image.
                        </template>
                        <template v-else>
                            The correct image is highlighted in green, and your selected image is highlighted in red.
                        </template>
                    </p>

                    <div class="mt-3 grid gap-3 sm:grid-cols-2">
                        <div class="rounded-xl border border-white/10 bg-black/20 p-3">
                            <div class="text-xs text-white/50">Your answer</div>
                            <div class="mt-1 text-sm font-semibold text-white">
                                {{ game3.result.value.answer.user_answer }}
                            </div>
                        </div>

                        <div class="rounded-xl border border-white/10 bg-black/20 p-3">
                            <div class="text-xs text-white/50">Correct answer</div>
                            <div class="mt-1 text-sm font-semibold text-[#e0608a]">
                                {{ game3.result.value.answer.correct_answer }}
                            </div>
                        </div>
                    </div>
                </div>

                <div class="mt-6 flex justify-end">
                    <button
                        v-if="!game3.result.value"
                        class="rounded-xl bg-[#8c0a42] px-6 py-2 text-sm font-semibold text-white transition hover:bg-[#a00d4e] disabled:opacity-40"
                        :disabled="!game3.selectedImageId.value || game3.submitting.value"
                        @click="handleSubmit"
                    >
                        {{ game3.submitting.value ? "Submitting…" : "Submit" }}
                    </button>

                    <button
                        v-else
                        class="rounded-xl bg-[#8c0a42] px-6 py-2 text-sm font-semibold text-zinc-100 transition hover:bg-[#a00d4e]"
                        @click="emit('round-complete', game3.result.value)"
                    >
                        Continue
                    </button>
                </div>
            </section>
        </template>
    </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useGame3 } from "../../composables/useGame3";
import type { SubmitResult } from "../../types/game";

const props = defineProps<{
    sessionId: string;
    round: number;
}>();

const emit = defineEmits<{
    (e: "round-complete", result: SubmitResult): void;
}>();

const game3 = useGame3();

onMounted(() => {
    game3.loadRoundData(props.sessionId, props.round);
});

function handleSelect(imageId: string) {
    if (game3.result.value) return;
    game3.selectedImageId.value = imageId;
}

function getSelectedImageId(): string | null {
    if (game3.result.value?.answer?.selected_image_id) {
        return game3.result.value.answer.selected_image_id;
    }
    return game3.selectedImageId.value;
}

function getCorrectImageId(): string | null {
    return game3.roundData.value?.correct_image_id ?? null;
}

function getImageState(imageId: string): "default" | "correct" | "wrong" {
    if (!game3.result.value) return "default";

    const selectedId = getSelectedImageId();
    const correctId = getCorrectImageId();

    if (correctId && imageId === correctId) return "correct";
    if (selectedId && imageId === selectedId && selectedId !== correctId) return "wrong";

    return "default";
}

function getImageCardClass(imageId: string): string {
    if (game3.result.value) {
        const state = getImageState(imageId);

        if (state === "correct") {
            return "border-green-500 bg-green-500/10";
        }

        if (state === "wrong") {
            return "border-red-500 bg-red-500/10";
        }

        return "border-white/10 bg-black/20";
    }

    return game3.selectedImageId.value === imageId
        ? "border-[#8c0a42] bg-[#8c0a42]/10"
        : "border-white/10 bg-black/20 hover:border-[#8c0a42]/50";
}

async function handleSubmit() {
    await game3.submit(props.sessionId, props.round);
}
</script>