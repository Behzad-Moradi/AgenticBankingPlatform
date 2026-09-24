export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
}

export interface RegisterResponse {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
}

export interface KnowledgeSource {
  source: string;
  page: number | null;
  chunk_index: number;
}

export interface InterruptInfo {
  action: string;
  card_id: number | null;
  last_four: string | null;
  account_type: string | null;
  full_name: string | null;
  date_of_birth: string | null;
  address: string | null;
  phone: string | null;
  licence_number: string | null;
  message: string;
}

export interface ChatRequest {
  message: string;
  thread_id: string;
}

export interface ChatResumeRequest {
  thread_id: string;
  approved: boolean;
}

export interface ChatResponse {
  message: string | null;
  thread_id: string;
  sources: KnowledgeSource[];
  interrupt: InterruptInfo | null;
  account_opening_stage: string | null;
  requires_document_upload: boolean;
}

export interface DocumentUploadResponse {
  message: string;
  thread_id: string;
  verified: boolean;
  account_opening_stage: string;
  requires_document_upload: boolean;
}

export interface ApiErrorBody {
  detail?: string | Array<{ loc?: Array<string | number>; msg?: string }>;
}
