import type { InterruptInfo, KnowledgeSource } from "./api";

export interface ConversationMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  sources?: KnowledgeSource[];
  interrupt?: InterruptInfo | null;
  requiresDocumentUpload?: boolean;
  createdAt: Date;
}
