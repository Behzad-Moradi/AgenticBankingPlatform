import type {
  ApiErrorBody,
  AuthToken,
  ChatRequest,
  ChatResponse,
  ChatResumeRequest,
  DocumentUploadResponse,
  RegisterRequest,
  RegisterResponse,
} from "../types/api";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "/api").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function formatError(body: ApiErrorBody | null, status: number): string {
  if (typeof body?.detail === "string") return body.detail;
  if (Array.isArray(body?.detail)) {
    return body.detail.map((item) => item.msg).filter(Boolean).join(" ") || `Request failed (${status}).`;
  }
  return status === 0
    ? "Unable to reach the banking service. Check that the backend is running."
    : `Request failed (${status}).`;
}

async function request<T>(path: string, init: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  } catch {
    throw new ApiError(formatError(null, 0), 0);
  }

  if (!response.ok) {
    let body: ApiErrorBody | null = null;
    try {
      body = (await response.json()) as ApiErrorBody;
    } catch {
      // Preserve the generic status message for non-JSON errors.
    }
    throw new ApiError(formatError(body, response.status), response.status);
  }

  return (await response.json()) as T;
}

export function login(email: string, password: string): Promise<AuthToken> {
  const body = new URLSearchParams({ username: email.trim().toLowerCase(), password });
  return request<AuthToken>("/auth/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
}

export function register(payload: RegisterRequest): Promise<RegisterResponse> {
  return request<RegisterResponse>("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...payload,
      first_name: payload.first_name.trim(),
      last_name: payload.last_name.trim(),
      email: payload.email.trim().toLowerCase(),
    }),
  });
}

export function sendMessage(payload: ChatRequest, token: string): Promise<ChatResponse> {
  return request<ChatResponse>(
    "/chat",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
    token,
  );
}

export function resumeChat(payload: ChatResumeRequest, token: string): Promise<ChatResponse> {
  return request<ChatResponse>(
    "/chat/resume",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
    token,
  );
}

export function uploadAccountDocument(
  threadId: string,
  file: File,
  token: string,
): Promise<DocumentUploadResponse> {
  const body = new FormData();
  body.append("file", file);
  return request<DocumentUploadResponse>(
    `/chat/account-opening/document?thread_id=${encodeURIComponent(threadId)}`,
    { method: "POST", body },
    token,
  );
}
