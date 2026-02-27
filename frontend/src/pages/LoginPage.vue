<template>
    <div class="main-layout">
        <div class="w-full max-w-4xl px-10">
            <div class="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl shadow-black/40">
                <div class="flex flex-col lg:flex-row min-h-137.5 lg:h-3/4">
                    <!-- Formulario -->
                    <div class="flex-1 p-4 sm:p-6 lg:p-8 flex flex-col justify-center order-2 lg:order-1">
                        <div class="max-w-md mx-auto w-full">
                            <h2 class="text-2xl font-bold mb-2 text-[#8c0a42]">Login</h2>
                            <p class="text-sm text-white/70 mb-6">Welcome! Log in to your account to continue.</p>
                            <n-form ref="formRef" :model="model" :rules="rules" @submit.prevent="onSubmit">
                                <div class="flex flex-col space-y-4 mb-6">
                                    <label for="email">
                                        <div class="text-sm text-white/70 mb-1">Email</div>
                                        <input type="text" id="email" v-model="model.email"
                                            placeholder="you@example.com"
                                            class="w-full border rounded-full px-3 py-2 border-white/20 bg-[#171717] text-white focus:outline-none focus:ring-1 focus:ring-[#8c0a42] focus:border-transparent" />
                                    </label>
                                    <label for="password">
                                        <div class="text-sm text-white/70 mb-1">Password</div>
                                        <input type="password" id="password" v-model="model.password"
                                            placeholder="Enter your password"
                                            class="w-full border rounded-full px-3 py-2 border-white/20 bg-[#171717] text-white focus:outline-none focus:ring-1 focus:ring-[#8c0a42] focus:border-transparent" />
                                    </label>
                                </div>
                                <button
                                    class="w-full bg-[#8c0a42] text-white py-2 px-4 rounded-full hover:bg-[#9c0b52] transition-colors disabled:opacity-30"
                                    :disabled="loading" @click="onSubmit">
                                    {{ loading ? "Logging in..." : "Log In" }}
                                </button>
                            </n-form>
                        </div>
                    </div>

                    <!-- Image container -->
                    <div
                        class="flex-1 bg-[#171717] relative overflow-hidden order-1 lg:order-2 min-h-75 sm:min-h-100 lg:min-h-0 rounded-2xl border border-white/10 shadow-sm shadow-white/10">
                        <div class="absolute inset-0 bg-cover bg-right bg-no-repeat"
                            style="background-image: url('/login-img.jpg')">
                            <div class="absolute inset-0 bg-red-200/10"></div>
                        </div>

                    </div>


                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useMessage, type FormInst, type FormRules, NForm, NFormItem, NInput } from "naive-ui";
import { useAuthStore } from "../stores/auth";
import { ApiError } from "../api/http";


const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const message = useMessage();

const formRef = ref<FormInst | null>(null);
const loading = ref(false);

const model = reactive({
    email: "",
    password: "",
});

const rules: FormRules = {
    email: [
        { required: true, message: "Email requerido", trigger: ["input", "blur"] },
        { type: "email", message: "Email inválido", trigger: ["blur"] },
    ],
    password: [{ required: true, message: "Password requerido", trigger: ["input", "blur"] }],
};

async function onSubmit() {
    try {
        await formRef.value?.validate();
        loading.value = true;

        await auth.login(model.email, model.password);

        const next = typeof route.query.next === "string" ? route.query.next : "/";
        router.replace(next);
    } catch (e) {
        if (e instanceof ApiError) {
            message.error(e.message);
        } else {
            if (!(e as any)?.errors) message.error("No se pudo iniciar sesión");
        }
    } finally {
        loading.value = false;
    }
}
</script>
