"""Fail closed against the reviewed positive-list and frozen public anchor bytes."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {".git", ".venv", "__pycache__", "receipts"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    listed = json.loads((ROOT / "RELEASE_FILES.json").read_text())
    assert listed["release"] == "book14-public-companion-v0.1.0"
    files = listed["files"]
    assert isinstance(files, dict) and files
    expected = set(files) | {"RELEASE_FILES.json"}
    actual = set()
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDE for part in rel.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"symlink forbidden: {rel}")
        if path.is_file():
            actual.add(rel.as_posix())
    if actual != expected:
        raise ValueError(f"release inventory mismatch; extra={sorted(actual-expected)} missing={sorted(expected-actual)}")
    for rel, digest in files.items():
        if len(digest) != 64 or sha(ROOT / rel) != digest:
            raise ValueError(f"release hash mismatch: {rel}")
    lines = (ROOT / "data/SHA256SUMS.txt").read_text().splitlines()
    anchor = {f"data/anchor/{name}.csv" for name in
              ("participants", "baseline", "followup_long", "registry", "design_colleges", "design_joint_pi")}
    summed = {}
    for line in lines:
        digest, rel = line.split("  ")
        if rel in summed:
            raise ValueError("duplicate sum")
        summed[rel] = digest
    if set(summed) != anchor:
        raise ValueError("wrong anchor list")
    for rel, digest in summed.items():
        if sha(ROOT / rel) != digest:
            raise ValueError(f"changed anchor: {rel}")
    with (ROOT / "data/DICTIONARY.csv").open(newline="") as stream:
        dictionary = list(csv.DictReader(stream))
    defined = {(row["file"], row["variable"]) for row in dictionary}
    actual_fields = set()
    for rel in anchor:
        with (ROOT / rel).open(newline="") as stream:
            reader = csv.DictReader(stream)
            actual_fields.update((rel, name) for name in reader.fieldnames)
            if not next(reader, None):
                raise ValueError("empty source")
    if defined != actual_fields or len(defined) != len(dictionary):
        raise ValueError("dictionary does not cover exactly the published columns")
    print(f"BOOK14_PUBLIC_RELEASE_OK files={len(files)} anchor=6 fields={len(defined)}")


if __name__ == "__main__":
    main()
