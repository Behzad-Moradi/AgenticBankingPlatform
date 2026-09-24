import { useState } from "react";
import { Chat } from "./components/Chat";
import { Login } from "./components/Login";
import { ApiError, login, register, resumeChat, sendMessage, uploadAccountDocument } from "./services/api";
import { clearStoredToken, createThreadId, getStoredToken, storeToken } from "./services/session";
import type { ChatResponse } from "./types/api";
import type { ConversationMessage } from "./types/chat";

function messageId(): string {
  return crypto.randomUUID();
}

export default function App() {
  const [token, setToken] = useState<string | null>(() => getStoredToken());
  const [threadId, setThreadId] = useState(() => createThreadId());
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function appendResponse(response: ChatResponse) {
    const content = response.message ?? (response.interrupt
      ? response.interrupt.action === "freeze_card"
        ? "A card security action needs your confirmation."
        : "This application is ready for a staff decision."
      : null);
    if (!content) return;
    setMessages((current) => [
      ...current,
      {
        id: messageId(),
        role: "assistant",
        content,
        sources: response.sources,
        interrupt: response.interrupt,
        requiresDocumentUpload: response.requires_document_upload,
        createdAt: new Date(),
      },
    ]);
  }

  function handleFailure(caught: unknown) {
    const message = caught instanceof Error ? caught.message : "Something went wrong.";
    setError(message);
    if (caught instanceof ApiError && caught.status === 401) {
      clearStoredToken();
      setToken(null);
    }
  }

  async function handleLogin(email: string, password: string) {
    const result = await login(email, password);
    storeToken(result.access_token);
    setToken(result.access_token);
  }

  async function handleRegister(firstName: string, lastName: string, email: string, password: string) {
    await register({ first_name: firstName, last_name: lastName, email, password });
    await handleLogin(email, password);
  }

  async function handleSend(content: string) {
    if (!token || loading) return;
    setMessages((current) => [...current, { id: messageId(), role: "user", content, createdAt: new Date() }]);
    setLoading(true);
    setError("");
    try {
      appendResponse(await sendMessage({ message: content, thread_id: threadId }, token));
    } catch (caught) {
      handleFailure(caught);
    } finally {
      setLoading(false);
    }
  }

  async function handleResume(approved: boolean) {
    if (!token || loading) return;
    setLoading(true);
    setError("");
    try {
      appendResponse(await resumeChat({ thread_id: threadId, approved }, token));
    } catch (caught) {
      handleFailure(caught);
      throw caught;
    } finally {
      setLoading(false);
    }
  }

  async function handleUpload(file: File) {
    if (!token || loading) return;
    setLoading(true);
    setError("");
    try {
      const response = await uploadAccountDocument(threadId, file, token);
      setMessages((current) => [...current, {
        id: messageId(),
        role: "assistant",
        content: response.message + (response.verified ? " You can now continue the application in the chat." : ""),
        requiresDocumentUpload: response.requires_document_upload,
        createdAt: new Date(),
      }]);
    } catch (caught) {
      handleFailure(caught);
      throw caught;
    } finally {
      setLoading(false);
    }
  }

  function newConversation() {
    setThreadId(createThreadId());
    setMessages([]);
    setError("");
  }

  function logout() {
    clearStoredToken();
    setToken(null);
    newConversation();
  }

  if (!token) return <Login onLogin={handleLogin} onRegister={handleRegister} />;

  return (
    <Chat
      messages={messages}
      threadId={threadId}
      loading={loading}
      error={error}
      onSend={handleSend}
      onResume={handleResume}
      onUpload={handleUpload}
      onNewConversation={newConversation}
      onLogout={logout}
    />
  );
}
