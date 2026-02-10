import { defineStore } from "pinia";
import type { User, LoginResponse } from "../api/auth";
import * as AuthAPI from "../api/auth";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as User | null,
    bootstrapped: false,
  }),
  getters: {
    isAuthed: (s) => !!s.user,
  },
  actions: {
    async bootstrap() {
      if (this.bootstrapped) return;
      try {
        const user = await AuthAPI.me();
        this.user = user;
      } catch {
        this.user = null;
      } finally {
        this.bootstrapped = true;
      }
    },

    async login(email: string, password: string) {
      const res: LoginResponse = await AuthAPI.login({ email, password });

      const { access_token: _token, token_type: _type, ...user } = res;
      this.user = user;
      this.bootstrapped = true;
    },

    async logout() {
      try {
        await AuthAPI.logout();
      } finally {
        this.user = null;
        this.bootstrapped = true;
      }
    },
  },
});
