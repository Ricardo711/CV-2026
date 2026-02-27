<template>
    <section class="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl shadow-black/40">
        <div>
            <h2 class="text-lg font-semibold">
                What marbling class belongs to your image?
            </h2>
            <p class="mt-1 text-sm text-white/70">
                Select one option before predicting.
            </p>
        </div>

        <div class="mt-4 grid gap-2 sm:grid-cols-2">
            <label v-for="opt in options" :key="opt" class="flex cursor-pointer items-center gap-2 rounded-xl
               border border-white/10 bg-black/20 px-3 py-2
               hover:border-[#8c0a42]/50 hover:bg-[#8c0a42]/10 transition">
                <input class="h-4 w-4 accent-[#8c0a42]" type="radio" name="marbling" :value="opt"
                    :checked="modelValue === opt" @change="onSelect(opt)" />
                <span class="text-sm">{{ opt }}</span>
            </label>
        </div>
    </section>
</template>

<script setup lang="ts">
import type { MarblingClass } from "../../api/predictions";

/* Props / Emits */

defineProps<{
    modelValue: MarblingClass | null;
    options: readonly MarblingClass[];
}>();

const emit = defineEmits<{
    (e: "update:modelValue", value: MarblingClass): void;
}>();

/* Handlers */

function onSelect(value: MarblingClass) {
    emit("update:modelValue", value);
}
</script>
