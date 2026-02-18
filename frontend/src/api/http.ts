export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(message: string, status: number, data: unknown) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
type BodyType = unknown | FormData;

async function readBody(res: Response) {
  if (res.status === 204) return null;

  const ct = res.headers.get("content-type") ?? "";
  if (ct.includes("application/json")) {
    const text = await res.text();
    if (!text.trim()) return null;
    return JSON.parse(text);
  }

  const text = await res.text();
  return text.trim() ? text : null;
}

// ✅ Base URL desde Vercel/Local
const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

function buildUrl(path: string) {
  // Si ya viene full URL (http...), no lo toques
  if (/^https?:\/\//i.test(path)) return path;

  // Asegura que path empiece con /
  const p = path.startsWith("/") ? path : `/${path}`;

  // Si no hay BASE_URL (por error), cae a relativo
  return BASE_URL ? `${BASE_URL}${p}` : p;
}

export async function api<T>(
  path: string,
  opts: {
    method?: HttpMethod;
    body?: BodyType;
    headers?: Record<string, string>;
  } = {},
): Promise<T> {
  const isFormData = opts.body instanceof FormData;

  const headers: Record<string, string> = {
    ...(opts.headers ?? {}),
  };

  // Solo setea JSON si NO es FormData y hay body
  if (!isFormData && opts.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  const url = buildUrl(path); // ✅ aquí armamos la URL final

  const res = await fetch(url, {
    method: opts.method ?? "GET",
    credentials: "include",
    headers,
    body:
      opts.body === undefined
        ? undefined
        : isFormData
          ? (opts.body as FormData)
          : JSON.stringify(opts.body),
  });

  const data = await readBody(res);

  if (!res.ok) {
    const msg =
      data && typeof data === "object" && "detail" in (data as any)
        ? String((data as any).detail)
        : `Request failed (${res.status})`;
    throw new ApiError(msg, res.status, data);
  }

  return data as T;
}
