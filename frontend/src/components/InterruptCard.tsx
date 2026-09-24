import type { InterruptInfo } from "../types/api";
import { ShieldIcon } from "./Icons";

interface InterruptCardProps {
  interrupt: InterruptInfo;
  loading: boolean;
  resolved: boolean;
  onDecision: (approved: boolean) => Promise<void>;
}

export function InterruptCard({ interrupt, loading, resolved, onDecision }: InterruptCardProps) {
  const isFreeze = interrupt.action === "freeze_card";
  const applicationDetails = [
    ["Account type", interrupt.account_type],
    ["Applicant", interrupt.full_name],
    ["Date of birth", interrupt.date_of_birth],
    ["Address", interrupt.address],
    ["Phone", interrupt.phone],
    ["Licence number", interrupt.licence_number],
  ].filter((detail): detail is [string, string] => Boolean(detail[1]));
  const title = isFreeze ? "Confirm card freeze" : "Staff review required";
  const approveLabel = isFreeze ? "Freeze card" : "Approve application";
  const rejectLabel = isFreeze ? "Keep card active" : "Reject application";

  return (
    <section className={`interrupt-card ${resolved ? "resolved" : ""}`}>
      <div className="interrupt-title"><span><ShieldIcon /></span><div><small>{isFreeze ? "Security check" : "Human-in-the-loop"}</small><strong>{title}</strong></div></div>
      <p>{interrupt.message}</p>
      {isFreeze && interrupt.last_four && <div className="card-pill">Card ending in <strong>•••• {interrupt.last_four}</strong></div>}
      {!isFreeze && applicationDetails.length > 0 && (
        <dl className="application-review">
          {applicationDetails.map(([label, value]) => (
            <div key={label}><dt>{label}</dt><dd>{value}</dd></div>
          ))}
        </dl>
      )}
      {resolved ? (
        <p className="resolved-label">Decision submitted</p>
      ) : (
        <div className="decision-actions">
          <button className="secondary-button" type="button" disabled={loading} onClick={() => onDecision(false)}>{rejectLabel}</button>
          <button className="danger-button" type="button" disabled={loading} onClick={() => onDecision(true)}>
            {loading ? <><span className="spinner dark" /> Processing…</> : approveLabel}
          </button>
        </div>
      )}
    </section>
  );
}
