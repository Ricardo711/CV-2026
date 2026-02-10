import { createRouter, createWebHistory } from "vue-router";
import LoginPage from "../pages/LoginPage.vue";
import HomePage from "../pages/HomePage.vue";
import { useAuthStore } from "../stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "login",
      component: LoginPage,
      meta: { public: true },
    },
    { path: "/", name: "home", component: HomePage },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();

  await auth.bootstrap();

  // Rutas públicas
  if (to.meta.public) {
    if (auth.isAuthed && to.name === "login") {
      return { name: "home" };
    }
    return true;
  }

  // Rutas privadas
  if (!auth.isAuthed) {
    return {
      name: "login",
      query: { next: to.fullPath },
    };
  }

  return true;
});

export default router;
