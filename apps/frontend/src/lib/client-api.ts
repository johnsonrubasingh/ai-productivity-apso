const PUBLIC_API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://localhost:8000/api/v1";
const IS_PRODUCTION = process.env.NODE_ENV === "production";

type ApiResult<T> =
  | {
      ok: true;
      status: number;
      data: T;
    }
  | {
      ok: false;
      status: number;
      error: string;
      details?: unknown;
    };

export async function postBackend<TResponse>(
  path: string,
  body: unknown,
  searchParams?: Record<string, string | boolean | number>,
): Promise<ApiResult<TResponse>> {
  const url = new URL(`${PUBLIC_API_BASE_URL}${path}`);
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 8000);

  Object.entries(searchParams ?? {}).forEach(([key, value]) => {
    url.searchParams.set(key, String(value));
  });

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(),
      },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    const payload = (await response.json().catch(() => null)) as unknown;

    if (!response.ok) {
      return {
        ok: false,
        status: response.status,
        error: `Backend returned ${response.status}`,
        details: payload,
      };
    }

    return {
      ok: true,
      status: response.status,
      data: payload as TResponse,
    };
  } catch (error) {
    return {
      ok: false,
      status: 0,
      error: error instanceof Error ? error.message : "Unable to reach backend",
    };
  } finally {
    clearTimeout(timeout);
  }
}

export async function getBackend<TResponse>(path: string): Promise<ApiResult<TResponse>> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 8000);

  try {
    const response = await fetch(`${PUBLIC_API_BASE_URL}${path}`, {
      headers: authHeaders(),
      signal: controller.signal,
    });
    const payload = (await response.json().catch(() => null)) as unknown;

    if (!response.ok) {
      return {
        ok: false,
        status: response.status,
        error: `Backend returned ${response.status}`,
        details: payload,
      };
    }

    return {
      ok: true,
      status: response.status,
      data: payload as TResponse,
    };
  } catch (error) {
    return {
      ok: false,
      status: 0,
      error: error instanceof Error ? error.message : "Unable to reach backend",
    };
  } finally {
    clearTimeout(timeout);
  }
}

export function saveAuthToken(token: string): void {
  if (typeof window === "undefined") {
    return;
  }
  window.sessionStorage.setItem("apso.auth_token", token.trim());
}

export function clearAuthToken(): void {
  if (typeof window === "undefined") {
    return;
  }
  window.sessionStorage.removeItem("apso.auth_token");
}

export function readAuthToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return window.sessionStorage.getItem("apso.auth_token");
}

function authHeaders(): Record<string, string> {
  const token = readAuthToken();
  if (token) {
    return { Authorization: `Bearer ${token}` };
  }

  if (!IS_PRODUCTION) {
    return {
      "X-APSO-Dev-User": "frontend-dev",
      "X-APSO-Dev-Tenant": "default",
      "X-APSO-Dev-Role": "admin",
    };
  }

  return {};
}
