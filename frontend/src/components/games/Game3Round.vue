<template>
    <div class="space-y-4">
        <!-- Loading -->
        <div v-if="game3.loading.value" class="flex items-center justify-center py-16">
            <div class="text-sm text-white/60">Loading images…</div>
        </div>

        <!-- Error -->
        <div v-else-if="game3.error.value"
            class="rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">
            {{ game3.error.value }}
        </div>

        <template v-else-if="game3.roundData.value">
            <!-- Images grid -->
            <section v-if="!game3.result.value"
                class="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl shadow-black/40">
                <!-- Instructions -->
                <h2 class="text-lg font-semibold text-white">Image Selection</h2>
                <p class="my-1 text-sm text-white/70">
                    Select the image that corresponds to
                    <span class="font-bold text-[#e0608a]">{{ game3.roundData.value.target_class }}</span>.
                </p>
                <div class="grid grid-cols-3 gap-4">
                    <button v-for="img in game3.roundData.value.images" :key="img.id"
                        class="overflow-hidden rounded-2xl border-2 transition aspect-square" :class="game3.selectedImageId.value === img.id
                            ? 'border-[#8c0a42] bg-[#8c0a42]/10'
                            : 'border-white/10 bg-black/20 hover:border-[#8c0a42]/50'"
                        @click="game3.selectedImageId.value = img.id">
                        <img v-if="img.image_url" :src="img.image_url" alt="Meat image option"
                            class="h-full w-full object-cover" />
                        <div v-else class="grid h-full place-items-center p-4">
                            <div class="text-3xl opacity-30">🥩</div>
                        </div>
                    </button>
                </div>

                <div class="mt-6 flex justify-end">
                    <button class="rounded-xl bg-[#8c0a42] px-6 py-2 text-white text-sm font-semibold
                               disabled:opacity-40 hover:bg-[#a00d4e] transition"
                        :disabled="!game3.selectedImageId.value || game3.submitting.value" @click="handleSubmit">
                        {{ game3.submitting.value ? "Submitting…" : "Submit" }}
                    </button>
                </div>
            </section>

            <!-- Result -->
            <section v-else class="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl shadow-black/40">
                <h2 class="text-lg font-semibold text-white">Result</h2>

                <div class="mt-4 flex items-center gap-3">
                    <div class="rounded-full px-4 py-1 text-sm font-bold" :class="game3.result.value.answer.is_correct
                        ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                        : 'bg-red-500/20 text-red-400 border border-red-500/30'">
                        {{ game3.result.value.answer.is_correct ? "Correct!" : "Incorrect" }}
                    </div>
                </div>

                <p class="mt-3 text-sm text-white/70">
                    The correct image was the one labeled
                    <span class="font-semibold text-[#e0608a]">{{ game3.roundData.value.target_class }}</span>.
                </p>

                <div class="mt-6 flex justify-end">
                    <button
                        class="rounded-xl bg-[#8c0a42] text-zinc-100 px-6 py-2 text-sm font-semibold hover:bg-[#a00d4e] transition"
                        @click="emit('round-complete', game3.result.value)">
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

/* Props / Emits */

const props = defineProps<{
    sessionId: string;
    round: number;
}>();

const emit = defineEmits<{
    (e: "round-complete", result: SubmitResult): void;
}>();

/* Composable */

const game3 = useGame3();

/* Lifecycle */

onMounted(() => {
    game3.loadRoundData(props.sessionId, props.round);
});

/* Handlers */

async function handleSubmit() {
    await game3.submit(props.sessionId, props.round);
}
</script>
