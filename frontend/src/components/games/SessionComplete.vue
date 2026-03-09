<template>
    <div class="mx-auto max-w-md text-center">
        <section class="rounded-2xl border border-white/10 bg-white/5 p-8 shadow-sm shadow-black/40">
            <h2 class="mt-4 text-2xl font-bold text-white">Session Complete!</h2>
            <p class="mt-2 text-sm text-white/60">You've completed all 6 rounds.</p>

            <!-- Score -->
            <div class="mt-6 rounded-2xl border border-[#8c0a42]/30 bg-[#8c0a42]/10 p-5">
                <div class="text-xs text-white/50 uppercase tracking-wider">Final Score</div>
                <div class="mt-2 text-4xl font-bold text-[#e0608a]">
                    {{ score }}
                    <span class="text-lg text-white/40">/ 4</span>
                </div>
                <div class="mt-1 text-xs text-white/50">
                    Scored on Games 1 &amp; 3 (2 rounds each)
                </div>
            </div>

            <button
                class="mt-6 w-full rounded-xl bg-[#8c0a42] px-6 py-3 text-white text-sm font-semibold hover:bg-[#a00d4e] transition"
                @click="emit('restart')"
            >
                Start New Session
            </button>
        </section>
    </div>
</template>

<script setup lang="ts">
/* Props / Emits */

defineProps<{
    score: number;
}>();

const emit = defineEmits<{
    (e: "restart"): void;
}>();
</script>
