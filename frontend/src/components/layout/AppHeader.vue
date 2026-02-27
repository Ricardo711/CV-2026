<template>
    <header class="sticky top-0 z-10 border-b border-white/10
           bg-[#171717]/80 backdrop-blur">
        <div class="mx-auto flex max-w-5xl items-center
             justify-between px-6 py-4">
            <!-- Left -->
            <div class="flex items-center gap-3">
                <div class="h-9 w-9 rounded-xl bg-[#8c0a42]
                 shadow-lg shadow-[#8c0a42]/30" />
                <div class="leading-tight">
                    <div class="text-sm text-white/70">
                        Image prediction model
                    </div>
                    <div class="text-lg font-semibold">
                        Training
                    </div>
                </div>
            </div>

            <!-- Right -->
            <div class="flex items-center gap-4">
                <div class="hidden text-right sm:block">
                    <div class="text-sm font-medium">
                        {{ displayName }}
                    </div>
                    <div class="text-xs text-white/60">
                        {{ email }}
                    </div>
                </div>

                <button type="button" class="rounded-xl border border-white/10
                 bg-white/5 px-4 py-2 text-sm font-medium
                 hover:bg-white/10 active:scale-[0.99]
                 transition" @click="$emit('logout')">
                    Log out
                </button>
            </div>
        </div>
    </header>
</template>

<script setup lang="ts">
/* Props / Emits */

defineProps<{
    displayName: string;
    email?: string;
}>();

defineEmits<{
    (e: "logout"): void;
}>();
</script>
