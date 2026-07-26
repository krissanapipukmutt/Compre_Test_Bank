import type { VisualAsset } from "./domain";

export const MISSING_VISUAL_WARNING =
  "This question is missing a required visual and cannot be answered reliably. / คำถามนี้ขาดภาพที่จำเป็นและไม่สามารถตอบได้อย่างน่าเชื่อถือ";

export function selectVisualAlt(
  asset: VisualAsset,
  language = document.documentElement.lang,
): string {
  return language.toLowerCase().startsWith("th")
    ? asset.alt_th
    : asset.alt_en;
}
