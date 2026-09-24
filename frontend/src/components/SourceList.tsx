import type { KnowledgeSource } from "../types/api";
import { FileIcon } from "./Icons";

export function SourceList({ sources }: { sources: KnowledgeSource[] }) {
  if (!sources.length) return null;

  return (
    <div className="sources">
      <p className="source-label">Sources</p>
      <div className="source-grid">
        {sources.map((source, index) => (
          <div className="source-card" key={`${source.source}-${source.chunk_index}-${index}`}>
            <span className="source-icon"><FileIcon /></span>
            <span>
              <strong>{source.source.split("/").pop()}</strong>
              <small>{source.page != null ? `Page ${source.page}` : "Knowledge base"} · Passage {source.chunk_index + 1}</small>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
