#!/usr/bin/env python3
"""Validate presence and traceability of Phase 4 architecture deliverables."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "01-system-requirements.md",
    "02-user-flows.md",
    "03-information-architecture.md",
    "04-data-model.md",
    "05-responsive-ui-design.md",
    "06-technical-architecture.md",
    "07-component-design.md",
    "08-testing-strategy.md",
    "09-implementation-plan.md",
    "10-acceptance-criteria.md",
]
TOKENS = {
    "01-system-requirements.md": ["no answer", "local", "Thai", "runtime"],
    "04-data-model.md": ["stable", "correct_answer", "localStorage"],
    "05-responsive-ui-design.md": ["320×568", "1440×900", "44×44", "safe-area"],
    "06-technical-architecture.md": ["React + Vite + TypeScript", "strict", "privacy"],
    "08-testing-strategy.md": ["Playwright", "1024×768", "overflow"],
    "09-implementation-plan.md": [f"Phase 5.{index}" for index in range(1, 9)],
    "10-acceptance-criteria.md": ["AC-01", "AC-23", "before submission"],
}


def main() -> int:
    errors: list[str] = []
    base = ROOT / "docs/architecture"
    for name in REQUIRED:
        path = base / name
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        if len(text) < 500:
            errors.append(f"underspecified {path.relative_to(ROOT)}")
        for token in TOKENS.get(name, []):
            if token not in text:
                errors.append(f"{name} missing traceability token: {token}")
    for error in errors:
        print(f"ERROR: {error}")
    print(f"Architecture validation: {'PASS' if not errors else 'FAIL'} ({len(errors)} errors)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

