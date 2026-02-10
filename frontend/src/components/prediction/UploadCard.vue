<template>
    <section class="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl shadow-black/40">
        <div class="flex items-start justify-between gap-4">
            <div>
                <h2 class="text-lg font-semibold">Upload Image</h2>
                <p class="mt-1 text-sm text-white/70">
                    Upload an image and answer the marbling question to create a prediction.
                </p>
            </div>
        </div>

        <label class="mt-5 flex cursor-pointer flex-col items-center justify-center rounded-2xl border
             border-dashed border-white/15 bg-white/5 p-6 text-center
             hover:border-[#8c0a42]/60 hover:bg-[#8c0a42]/10 transition">
            <input ref="fileInput" class="hidden" type="file" accept="image/*" @change="onChange" />

            <div class="flex items-center gap-3">
                <div class="grid h-10 w-10 place-items-center rounded-xl bg-[#8c0a42]
                 shadow-lg shadow-[#8c0a42]/30">
                    <span class="text-sm font-bold">↑</span>
                </div>

                <div>
                    <div class="text-sm font-semibold">Select an image</div>
                    <div class="text-xs text-white/60">or drag it here</div>
                </div>
            </div>

            <div class="mt-4 text-xs text-white/50">
                Max. recommended: 5MB. Formats: JPG, PNG, WEBP
            </div>
        </label>
    </section>
</template>

<script setup lang="ts">
import { ref } from "vue";

/* Emits */

const emit = defineEmits<{
    (e: "file-selected", file: File): void;
}>();

/* Refs */

const fileInput = ref<HTMLInputElement | null>(null);

/* Handlers */

function onChange(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];

    if (!file) return;

    emit("file-selected", file);

    // Permite volver a seleccionar el mismo archivo
    if (fileInput.value) {
        fileInput.value.value = "";
    }
}
</script>
