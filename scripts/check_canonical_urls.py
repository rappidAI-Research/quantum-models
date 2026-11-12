"""Check canonical Quantum navigation URLs while retaining versioned schema IDs."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_OWNER = "rappidAI-Research"
CANONICAL_REPO = "quantum-models"
SLUG_PATTERN = re.compile(
    r"github\.com/([A-Za-z0-9][A-Za-z0-9-]*)/(quantum-models|lumen-quantum)"
    r"(?:\.git)?(?=$|[/#?\s)\]}>\"'\x60,;])"
)
TEXT_SUFFIXES = {
    ".cfg",
    ".cff",
    ".json",
    ".jsonl",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [ROOT / item for item in result.stdout.splitlines() if item]


def non_canonical_references() -> list[str]:
    problems: list[str] = []
    for path in tracked_files():
        if path.suffix.lower() not in TEXT_SUFFIXES or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            # A published schema identity is not a browser link. Renaming it would
            # change the contract rather than repair navigation.
            if path.parent == ROOT / "schemas" and re.match(r'\s*"\$id"\s*:', line):
                continue
            for match in SLUG_PATTERN.finditer(line):
                owner, repository = match.groups()
                if owner.lower() != CANONICAL_OWNER.lower() or repository != CANONICAL_REPO:
                    problems.append(
                        f"{path.relative_to(ROOT)}:{line_number}: "
                        f"non-canonical repository '{owner}/{repository}' "
                        f"(expected '{CANONICAL_OWNER}/{CANONICAL_REPO}')"
                    )
    return problems


def main() -> int:
    problems = non_canonical_references()
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        return 1
    print("Canonical repository URL check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
