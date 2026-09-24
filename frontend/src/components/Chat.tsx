import { useEffect, useRef, useState, type FormEvent } from "react";
import type { ConversationMessage } from "../types/chat";
import { DocumentUpload } from "./DocumentUpload";
import { InterruptCard } from "./InterruptCard";
import { AgentNetworkIcon, LogoutIcon, PlusIcon, SendIcon, ShieldIcon, SparkIcon } from "./Icons";
import { SourceList } from "./SourceList";

interface ChatProps {
  messages: ConversationMessage[];
  threadId: string;
  loading: boolean;
  error: string;
  onSend: (message: string) => Promise<void>;
  onResume: (approved: boolean) => Promise<void>;
  onUpload: (file: File) => Promise<void>;
  onNewConversation: () => void;
  onLogout: () => void;
}

const prompts = [
  "Show my accounts",
  "What are the account fees?",
  "I want to open a savings account",
  "Help with a suspicious card transaction",
];

function needsDocument(messages: ConversationMessage[]): boolean {
  const last = [...messages].reverse().find((message) => message.role === "assistant");
  return Boolean(last?.requiresDocumentUpload);
}

function initials(role: ConversationMessage["role"]) {
  return role === "user" ? "You" : "AI";
}

export function Chat({ messages, threadId, loading, error, onSend, onResume, onUpload, onNewConversation, onLogout }: ChatProps) {
  const [draft, setDraft] = useState("");
  const [resolvedInterrupts, setResolvedInterrupts] = useState<Set<string>>(new Set());
  const endRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, loading, error]);

  async function submit(event?: FormEvent) {
    event?.preventDefault();
    const value = draft.trim();
    if (!value || loading) return;
    setDraft("");
    await onSend(value);
    textRef.current?.focus();
  }

  async function decide(messageId: string, approved: boolean) {
    try {
      await onResume(approved);
      setResolvedInterrupts((current) => new Set(current).add(messageId));
    } catch {
      // The parent displays the API error and leaves the decision available to retry.
    }
  }

  const latestInterrupt = [...messages].reverse().find((message) => message.interrupt && !resolvedInterrupts.has(message.id));
  const inputDisabled = loading || Boolean(latestInterrupt);

  return (
    <main className="app-shell">
      <header className="app-header">
        <div className="brand"><span className="brand-mark"><AgentNetworkIcon /></span><span>Agentic Banking Platform</span><small>Assistant</small></div>
        <div className="header-actions">
          <div className="status-badge"><i /> Secure session</div>
          <button className="icon-text-button" type="button" onClick={onNewConversation} disabled={loading} title="Start a new conversation"><PlusIcon /> <span>New chat</span></button>
          <button className="icon-button" type="button" onClick={onLogout} disabled={loading} aria-label="Sign out" title="Sign out"><LogoutIcon /></button>
        </div>
      </header>

      <section className="chat-layout">
        <div className="conversation">
          <div className="conversation-heading">
            <div><span className="eyebrow dark">Personal banking</span><h1>How can we help?</h1></div>
            <span className="thread-label" title={threadId}>Conversation {threadId.slice(0, 8)}</span>
          </div>

          <div className="message-list" aria-live="polite">
            {messages.length === 0 && (
              <div className="welcome-state">
                <div className="welcome-icon"><SparkIcon /></div>
                <h2>Welcome to your banking assistant</h2>
                <p>Ask about your accounts, banking information, card security, or start a new account application.</p>
                <div className="prompt-grid">
                  {prompts.map((prompt) => <button type="button" key={prompt} onClick={() => onSend(prompt)} disabled={loading}>{prompt}<span>→</span></button>)}
                </div>
              </div>
            )}

            {messages.map((message) => (
              <article className={`message-row ${message.role}`} key={message.id}>
                <div className="avatar">{message.role === "assistant" ? <SparkIcon /> : initials(message.role)}</div>
                <div className="message-content">
                  <div className="message-meta"><strong>{message.role === "assistant" ? "Agentic Banking Platform Assistant" : "You"}</strong><time>{message.createdAt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</time></div>
                  <div className="message-bubble">{message.content}</div>
                  {message.sources && <SourceList sources={message.sources} />}
                  {message.interrupt && <InterruptCard interrupt={message.interrupt} loading={loading} resolved={resolvedInterrupts.has(message.id)} onDecision={(approved) => decide(message.id, approved)} />}
                </div>
              </article>
            ))}

            {needsDocument(messages) && !loading && <DocumentUpload loading={loading} onUpload={onUpload} />}
            {loading && <div className="thinking"><span /><span /><span /><em>Assistant is working</em></div>}
            {error && <div className="alert error chat-error" role="alert">{error}</div>}
            <div ref={endRef} />
          </div>

          <form className="composer" onSubmit={submit}>
            <textarea
              ref={textRef}
              rows={1}
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); void submit(); }
              }}
              placeholder={latestInterrupt ? "Respond to the approval request above" : "Message your banking assistant…"}
              disabled={inputDisabled}
              aria-label="Chat message"
            />
            <button type="submit" aria-label="Send message" disabled={!draft.trim() || inputDisabled}><SendIcon /></button>
            <p><ShieldIcon /> AI can make mistakes. Review banking details before acting.</p>
          </form>
        </div>
      </section>
    </main>
  );
}
