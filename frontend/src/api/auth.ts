import { api } from "./http";

export type User = {
  id: string;
  email: string;
  full_name: string | null;
  created_at: string; // ISO
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type LoginResponse = User & {
  access_token: string;
  token_type: "bearer" | string;
};

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  return api<LoginResponse>("/auth/login", { method: "POST", body: payload });
}

export async function me(): Promise<User> {
  return api<User>("/auth/me");
}

export async function logout(): Promise<void> {
  await api<null>("/auth/logout", { method: "POST" });
}

