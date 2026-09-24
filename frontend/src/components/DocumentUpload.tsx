import { useRef, useState, type ChangeEvent, type DragEvent } from "react";
import { FileIcon, LockIcon, UploadIcon } from "./Icons";

interface DocumentUploadProps {
  loading: boolean;
  onUpload: (file: File) => Promise<void>;
}

const allowed = ["image/jpeg", "image/png", "application/pdf"];

export function DocumentUpload({ loading, onUpload }: DocumentUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState("");

  function choose(candidate?: File) {
    if (!candidate) return;
    if (!allowed.includes(candidate.type)) {
      setError("Choose a JPEG, PNG, or PDF file.");
      return;
    }
    setError("");
    setFile(candidate);
  }

  function drop(event: DragEvent) {
    event.preventDefault();
    setDragging(false);
    choose(event.dataTransfer.files[0]);
  }

  function change(event: ChangeEvent<HTMLInputElement>) {
    choose(event.target.files?.[0]);
  }

  return (
    <section className="upload-card" aria-label="Driver licence upload">
      <div className="upload-heading"><span><UploadIcon /></span><div><strong>Identity verification</strong><p>Upload the driver licence requested above.</p></div></div>
      <button
        type="button"
        className={`drop-zone ${dragging ? "dragging" : ""}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(event) => { event.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={drop}
      >
        <UploadIcon />
        <span>{file ? "Choose a different file" : "Drop your licence here or browse"}</span>
        <small>JPEG, PNG, or PDF</small>
      </button>
      <input ref={inputRef} className="visually-hidden" type="file" accept="image/jpeg,image/png,application/pdf" onChange={change} />
      {file && <div className="selected-file"><FileIcon /><span><strong>{file.name}</strong><small>{(file.size / 1024 / 1024).toFixed(2)} MB</small></span></div>}
      {error && <p className="inline-error">{error}</p>}
      <button
        className="primary-button compact"
        type="button"
        disabled={!file || loading}
        onClick={() => {
          if (file) void onUpload(file).catch(() => undefined);
        }}
      >
        {loading ? <><span className="spinner" /> Verifying…</> : "Upload and verify"}
      </button>
      <p className="secure-caption"><LockIcon /> Sent securely to the banking service for verification.</p>
    </section>
  );
}
