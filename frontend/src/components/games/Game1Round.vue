<template>
    <div class="space-y-4">
        <!-- Loading -->
        <div v-if="game1.loading.value" class="flex items-center justify-center py-16">
            <div class="text-sm text-white/60">Loading image…</div>
        </div>

        <!-- Error -->
        <div v-else-if="game1.error.value"
            class="rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">
            {{ game1.error.value }}
        </div>

        <template v-else-if="game1.roundData.value">
            <!-- Image -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <section class="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-sm shadow-black/40">
                    <h2 class="text-lg font-semibold text-white">Classify this image</h2>
                    <p class="mt-1 text-sm text-white/70">Select the marbling class that best matches.</p>

                    <div
                        class="mt-4 aspect-video w-full overflow-hidden rounded-2xl border border-white/10 bg-black/30">
                        <img v-if="game1.roundData.value.image.image_url" :src="game1.roundData.value.image.image_url"
                            alt="Classify this meat image" class="h-full w-full object-contain" />
                        <div v-else class="grid h-full place-items-center">
                            <div class="text-center">
                                <div class="text-4xl opacity-30">🥩</div>
                                <div class="mt-2 text-sm text-white/50">Placeholder image</div>
                            </div>
                        </div>
                    </div>
                </section>

                <div>
                    <!-- Class selector (only before submitting) -->
                    <section v-if="!game1.result.value"
                        class="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-sm shadow-black/40">
                        <h2 class="text-lg font-semibold text-white">Select a class</h2>
                        <div class="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                            <label v-for="opt in NINE_CLASSES" :key="opt" class="flex cursor-pointer items-center gap-2 rounded-xl text-zinc-400 border border-white/10 bg-black/20 px-3 py-2
                                        hover:border-[#8c0a42]/50 hover:bg-[#8c0a42]/10 hover:text-white transition"
                                :class="{ 'border-[#8c0a42] bg-[#8c0a42]/10 text-white': game1.selectedClass.value === opt }">
                                <input class="h-4 w-4 accent-[#8c0a42]" type="radio" name="game1-class" :value="opt"
                                    :checked="game1.selectedClass.value === opt"
                                    @change="game1.selectedClass.value = opt" />
                                <span class="text-sm">{{ opt }}</span>
                            </label>
                        </div>

                        <div class="mt-6 flex justify-end">
                            <button class="rounded-xl bg-[#8c0a42] px-6 py-2 text-white text-sm font-semibold
                                        disabled:opacity-40 hover:bg-[#a00d4e] transition"
                                :disabled="!game1.selectedClass.value || game1.submitting.value" @click="handleSubmit">
                                {{ game1.submitting.value ? "Submitting…" : "Submit" }}
                            </button>
                        </div>
                    </section>

                    <!-- Result -->
                    <section v-else class="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-sm shadow-black/40">
                        <h2 class="text-lg font-semibold text-white">Result</h2>

                        <div class="mt-4 flex items-center gap-3">
                            <div class="rounded-full px-4 py-1 text-sm font-bold" :class="game1.result.value.answer.is_correct
                                ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                                : 'bg-red-500/20 text-red-400 border border-red-500/30'">
                                {{ game1.result.value.answer.is_correct ? "Correct!" : "Incorrect" }}
                            </div>
                        </div>

                        <div class="mt-4 grid gap-3 sm:grid-cols-2">
                            <div class="rounded-xl border border-white/10 bg-black/20 p-3">
                                <div class="text-xs text-white/50">Your answer</div>
                                <div class="mt-1 text-sm font-semibold text-white">
                                    {{ game1.result.value.answer.user_answer }}
                                </div>
                            </div>
                            <div class="rounded-xl border border-white/10 bg-black/20 p-3">
                                <div class="text-xs text-white/50">Correct answer</div>
                                <div class="mt-1 text-sm font-semibold text-[#e0608a]">
                                    {{ game1.result.value.answer.correct_answer }}
                                </div>
                            </div>
                        </div>

                        <div class="mt-6 flex justify-end">
                            <button
                                class="rounded-xl bg-[#8c0a42] text-zinc-100 px-6 py-2 text-sm font-semibold hover:bg-[#a00d4e] transition"
                                @click="emit('round-complete', game1.result.value)">
                                Continue
                            </button>
                        </div>
                    </section>
                </div>
            </div>
        </template>
    </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useGame1 } from "../../composables/useGame1";
import { NINE_CLASSES, type SubmitResult } from "../../types/game";

/* Props / Emits */

const props = defineProps<{
    sessionId: string;
    round: number;
}>();

const emit = defineEmits<{
    (e: "round-complete", result: SubmitResult): void;
}>();

/* Composable */

const game1 = useGame1();

/* Lifecycle */

onMounted(() => {
    game1.loadRoundData(props.sessionId, props.round);
});

/* Handlers */

async function handleSubmit() {
    await game1.submit(props.sessionId, props.round);
}
</script>