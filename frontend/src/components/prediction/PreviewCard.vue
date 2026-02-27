<template>
    <section class="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl shadow-black/40">
        <div class="flex items-start justify-between gap-4">
            <div>
                <h2 class="text-lg font-semibold">Preview</h2>
            </div>

            <div class="h-2.5 w-2.5 rounded-full" :class="file ? 'bg-[#8c0a42]' : 'bg-white/20'" aria-hidden="true" />
        </div>

        <div class="mt-5">
            <div class="aspect-6/3 w-full overflow-hidden rounded-2xl
               border border-white/10 bg-black/30">
                <img v-if="previewUrl" :src="previewUrl" alt="Image preview" class="h-full w-full object-contain" />

                <div v-else class="grid h-full w-full place-items-center">
                    <div class="text-center">
                        <div class="text-sm font-semibold text-white/70">No image</div>
                        <div class="mt-1 text-xs text-white/50">
                            Upload an image to see the preview here.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>

<script setup lang="ts">
/* Props */

defineProps<{
    file: File | null;
    previewUrl: string | null;
}>();
</script>
