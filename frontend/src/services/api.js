const BASE = import.meta.env.VITE_API_BASE_URL;

export async function apiFetch(path, options = {}) {
  return fetch(`${BASE}${path}`, {
    credentials: "include",
    ...options,
  });
}
