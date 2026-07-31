import type { ReactNode } from "react";
import type {
  AnswerStatus,
  Confidence,
  SourceReference,
} from "../domain";
import { answerStatusLabel } from "../engine";

export function Icon({
  name,
  size = 20,
}: {
  name:
    | "home"
    | "library"
    | "practice"
    | "mock"
    | "progress"
    | "menu"
    | "close"
    | "bookmark"
    | "search"
    | "arrow"
    | "clock"
    | "check"
    | "warning";
  size?: number;
}) {
  const paths: Record<typeof name, ReactNode> = {
    home: <path d="m3 11 9-8 9 8v9a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1Z" />,
    library: (
      <>
        <path d="M4 4h5v16H4zM10.5 4h4v16h-4zM16 5l3.5-1 3.8 14.5-3.5 1z" />
      </>
    ),
    practice: (
      <>
        <path d="M5 4h14v17H5z" />
        <path d="M8 2h8v4H8zM8 10h8M8 14h5" />
      </>
    ),
    mock: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M12 7v5l3 2" />
      </>
    ),
    progress: (
      <>
        <path d="M4 20V10M10 20V4M16 20v-7M22 20V7" />
      </>
    ),
    menu: <path d="M4 7h16M4 12h16M4 17h16" />,
    close: <path d="m6 6 12 12M18 6 6 18" />,
    bookmark: <path d="M6 3h12v18l-6-4-6 4z" />,
    search: (
      <>
        <circle cx="11" cy="11" r="7" />
        <path d="m16 16 5 5" />
      </>
    ),
    arrow: <path d="m9 5 7 7-7 7" />,
    clock: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M12 7v5l3 2" />
      </>
    ),
    check: <path d="m5 12 4 4L19 6" />,
    warning: (
      <>
        <path d="m12 3 10 18H2Z" />
        <path d="M12 9v5M12 17.5v.5" />
      </>
    ),
  };
  return (
    <svg
      aria-hidden="true"
      className="icon"
      fill="none"
      height={size}
      viewBox="0 0 24 24"
      width={size}
    >
      {paths[name]}
    </svg>
  );
}

export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: "neutral" | "success" | "warning" | "danger" | "teal";
}) {
  return <span className={`badge badge--${tone}`}>{children}</span>;
}

export function StatusBadge({ status }: { status: AnswerStatus }) {
  const tone =
    status === "verified_from_course_material" ||
    status === "verified_from_external_source"
      ? "success"
      : status === "strongly_supported_by_external_source" ||
          status === "probabilistic_recommendation"
        ? "warning"
        : "danger";
  const [english, thai] = answerStatusLabel(status).split(" · ");
  return (
    <Badge tone={tone}>
      {english}
      {thai ? <span lang="th"> · {thai}</span> : null}
    </Badge>
  );
}

export function ConfidenceBadge({
  confidence,
}: {
  confidence: Confidence;
}) {
  const tone =
    confidence === "high"
      ? "success"
      : confidence === "medium"
        ? "warning"
        : "danger";
  return <Badge tone={tone}>{confidence} confidence</Badge>;
}

export function AcademicNotice({
  title,
  children,
  severity = "warning",
}: {
  title: ReactNode;
  children: ReactNode;
  severity?: "warning" | "danger" | "info";
}) {
  return (
    <aside className={`notice notice--${severity}`} role="note">
      <span className="notice__icon">
        <Icon name="warning" />
      </span>
      <div>
        <strong>{title}</strong>
        <div className="notice__body">{children}</div>
      </div>
    </aside>
  );
}

export function BookmarkButton({
  active,
  label,
  onClick,
}: {
  active: boolean;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      aria-pressed={active}
      className={`icon-button bookmark-button ${active ? "is-active" : ""}`}
      onClick={onClick}
      title={label}
      type="button"
    >
      <Icon name="bookmark" />
      <span className="sr-only">{label}</span>
    </button>
  );
}

export function SourceList({
  sources,
  compact = false,
}: {
  sources: SourceReference[];
  compact?: boolean;
}) {
  return (
    <div className={`source-list ${compact ? "source-list--compact" : ""}`}>
      <h3>
        Sources <span lang="th">· แหล่งอ้างอิง</span>
      </h3>
      <ul>
        {sources.map((source) => (
          <li key={source.source_reference_id}>
            <code>{source.file_id}</code>
            <code data-language="th">{source.relative_path}</code>
            <span>
              {source.locator_end
                ? `pages/slides ${source.locator_start}–${source.locator_end}`
                : "whole document / slide deck"}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function EmptyState({
  title,
  children,
  action,
}: {
  title: string;
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="empty-state">
      <span className="empty-state__mark">∅</span>
      <h2>{title}</h2>
      <div>{children}</div>
      {action}
    </div>
  );
}

export function ConfirmDialog({
  open,
  title,
  children,
  confirmLabel,
  danger = false,
  onConfirm,
  onCancel,
}: {
  open: boolean;
  title: string;
  children: ReactNode;
  confirmLabel: string;
  danger?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  if (!open) return null;
  return (
    <div className="dialog-backdrop" onMouseDown={onCancel}>
      <section
        aria-labelledby="confirm-title"
        aria-modal="true"
        className="dialog"
        onMouseDown={(event) => event.stopPropagation()}
        role="dialog"
      >
        <h2 id="confirm-title">{title}</h2>
        <div className="dialog__body">{children}</div>
        <div className="dialog__actions">
          <button className="button button--ghost" onClick={onCancel} type="button">
            Cancel
          </button>
          <button
            className={`button ${danger ? "button--danger" : "button--primary"}`}
            onClick={onConfirm}
            type="button"
          >
            {confirmLabel}
          </button>
        </div>
      </section>
    </div>
  );
}
