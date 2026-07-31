import {
  useEffect,
  useRef,
  useState,
  type MouseEvent as ReactMouseEvent,
  type ReactNode,
} from "react";
import { createPortal } from "react-dom";
import type { VisualAsset } from "../domain";
import { selectVisualAlt } from "../visual";

function VisualLightbox({
  asset,
  label,
  ariaLabel,
  compact = false,
  onEssentialError,
}: {
  asset: VisualAsset;
  label: ReactNode;
  ariaLabel: string;
  compact?: boolean;
  onEssentialError: () => void;
}) {
  const [open, setOpen] = useState(false);
  const [zoom, setZoom] = useState(1);
  const openerRef = useRef<HTMLButtonElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const alt = selectVisualAlt(asset);

  const close = () => {
    setOpen(false);
    setZoom(1);
    window.setTimeout(() => openerRef.current?.focus(), 0);
  };

  useEffect(() => {
    if (!open) return;
    closeRef.current?.focus();
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        close();
      }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open]);

  const stopLabelActivation = (event: ReactMouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    event.stopPropagation();
    setOpen(true);
  };

  return (
    <>
      {compact ? (
        <button
          className="button button--secondary question-visual__reference-button"
          onClick={stopLabelActivation}
          ref={openerRef}
          type="button"
        >
          {label}
        </button>
      ) : (
        <figure
          className="question-visual"
          data-asset-id={asset.asset_id}
          data-testid="question-visual"
        >
          <div className="question-visual__preview">
            <img
              alt={alt}
              height={asset.height}
              loading="eager"
              onError={asset.is_essential ? onEssentialError : undefined}
              src={asset.public_path}
              width={asset.width}
            />
          </div>
          <figcaption>
            <span className="question-visual__caption">
              <span>{asset.caption_en}</span>
              <small lang="th">{asset.caption_th}</small>
            </span>
            <button
              className="question-visual__enlarge"
              onClick={stopLabelActivation}
              ref={openerRef}
              type="button"
            >
              Tap to enlarge <span lang="th">/ แตะเพื่อขยาย</span>
            </button>
          </figcaption>
        </figure>
      )}

      {open
        ? createPortal(
            <div className="visual-modal-backdrop" onMouseDown={close}>
              <section
                aria-label={ariaLabel}
                aria-modal="true"
                className="visual-modal"
                onMouseDown={(event) => event.stopPropagation()}
                role="dialog"
              >
                <header className="visual-modal__header">
                  <div>
                    <strong>{label}</strong>
                    <small>
                      Zoom and pan <span lang="th">/ ขยายและเลื่อนดู</span>
                    </small>
                  </div>
                  <button
                    aria-label="Close image viewer"
                    className="visual-modal__close"
                    onClick={close}
                    ref={closeRef}
                    type="button"
                  >
                    ×
                  </button>
                </header>
                <div className="visual-modal__viewport" data-testid="visual-viewport">
                  <img
                    alt={alt}
                    onError={asset.is_essential ? onEssentialError : undefined}
                    src={asset.public_path}
                    style={{ transform: `scale(${zoom})` }}
                  />
                </div>
                <footer className="visual-modal__controls">
                  <button
                    aria-label="Zoom out"
                    disabled={zoom <= 0.75}
                    onClick={() =>
                      setZoom((current) => Math.max(0.75, current - 0.25))
                    }
                    type="button"
                  >
                    −
                  </button>
                  <output aria-live="polite">{Math.round(zoom * 100)}%</output>
                  <button
                    aria-label="Zoom in"
                    disabled={zoom >= 3}
                    onClick={() =>
                      setZoom((current) => Math.min(3, current + 0.25))
                    }
                    type="button"
                  >
                    +
                  </button>
                  <button onClick={() => setZoom(1)} type="button">
                    Reset <span lang="th">/ รีเซ็ต</span>
                  </button>
                </footer>
              </section>
            </div>,
            document.body,
          )
        : null}
    </>
  );
}

export function QuestionVisuals({
  assets,
  includeReference = false,
  onEssentialError,
}: {
  assets: VisualAsset[];
  includeReference?: boolean;
  onEssentialError: () => void;
}) {
  const inlineAssets = assets.filter(
    (asset) => asset.placement !== "full_question_reference",
  );
  const reference = includeReference
    ? assets.find((asset) => asset.placement === "full_question_reference")
    : undefined;

  if (inlineAssets.length === 0 && !reference) return null;
  return (
    <section
      aria-label="Question visual material"
      className="question-visuals"
    >
      {inlineAssets.map((asset) => (
        <VisualLightbox
          asset={asset}
          ariaLabel="Question visual"
          key={asset.asset_id}
          label={
            <>
              Question visual <span lang="th">/ ภาพประกอบคำถาม</span>
            </>
          }
          onEssentialError={onEssentialError}
        />
      ))}
      {reference ? (
        <VisualLightbox
          asset={reference}
          ariaLabel="View original question image"
          compact
          label={
            <>
              View original question image{" "}
              <span lang="th">/ ดูภาพโจทย์ต้นฉบับ</span>
            </>
          }
          onEssentialError={onEssentialError}
        />
      ) : null}
    </section>
  );
}
