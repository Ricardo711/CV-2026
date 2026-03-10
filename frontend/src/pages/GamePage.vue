<template>
    <AppHeader :display-name="displayName" :email="auth.user?.email" @logout="onLogout" />

    <div class="mx-auto space-y-4 p-4">
        <!-- Loading session -->
        <div v-if="gs.loading.value && !gs.session.value" class="flex items-center justify-center py-20">
            <div class="text-sm text-white/60">Starting session…</div>
        </div>

        <!-- Error creating session -->
        <div v-else-if="gs.error.value && !gs.session.value"
            class="rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">
            {{ gs.error.value }}
            <button class="ml-3 underline" @click="gs.startSession()">Retry</button>
        </div>

        <template v-else-if="gs.session.value">
            <!-- Session complete -->
            <SessionComplete v-if="gs.isComplete.value" :score="gs.score.value" @restart="handleRestart" />

            <template v-else>
                <!-- Progress indicator -->
                <RoundProgress :current-round="gs.currentRound.value" :total-rounds="TOTAL_ROUNDS"
                    :game-type="gs.currentGameType.value" />

                <!-- Active game component — keyed to force remount on round change -->
                <Game1Round v-if="gs.currentGameType.value === 1" :key="`g1-r${gs.currentRound.value}`"
                    :session-id="gs.sessionId.value!" :round="gs.currentRound.value"
                    @round-complete="gs.onRoundComplete" />
                <Game3Round v-else-if="gs.currentGameType.value === 3" :key="`g3-r${gs.currentRound.value}`"
                    :session-id="gs.sessionId.value!" :round="gs.currentRound.value"
                    @round-complete="gs.onRoundComplete" />
                <Game2Round v-else-if="gs.currentGameType.value === 2" :key="`g2-r${gs.currentRound.value}`"
                    :session-id="gs.sessionId.value!" :round="gs.currentRound.value"
                    @round-complete="gs.onRoundComplete" />
            </template>
        </template>
    </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import { onMounted, computed } from "vue";
import { useGameSession } from "../composables/useGameSession";
import { TOTAL_ROUNDS } from "../types/game";
import RoundProgress from "../components/games/RoundProgress.vue";
import Game1Round from "../components/games/Game1Round.vue";
import Game2Round from "../components/games/Game2Round.vue";
import Game3Round from "../components/games/Game3Round.vue";
import SessionComplete from "../components/games/SessionComplete.vue";
import AppHeader from "../components/layout/AppHeader.vue";
import { useAuthStore } from "../stores/auth";

const gs = useGameSession();
const auth = useAuthStore();
const router = useRouter();

onMounted(() => {
    gs.startSession();
});

async function handleRestart() {
    await gs.startSession();
}

const displayName = computed(() => {
    return auth.user?.full_name || auth.user?.email || "User";
});

/* Actions */

async function onLogout() {
    await auth.logout();
    router.replace({ name: "login" });
}
</script>