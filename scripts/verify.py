"""Compare published worked examples with expected values and independent R."""
import csv
import importlib.util
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def compare(name, values, expected):
    if set(values) != set(expected):
        raise ValueError(f"{name}: metric keys disagree")
    for key, target in expected.items():
        value = values[key]
        if not math.isclose(float(value), float(target), rel_tol=0, abs_tol=1e-10):
            raise ValueError(f"{name}: {key} {value} != {target}")


def main():
    module("scripts/check_release.py", "release_check").main()
    expected = json.loads((ROOT / "expected/results.json").read_text())
    standard = module("examples/stdlib_route.py", "standard").calculate()
    numpy = module("examples/numpy_route.py", "vector").calculate()
    compare("standard library", standard, expected)
    compare("NumPy", numpy, expected)
    if "--base-r" in sys.argv:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "base-r.tsv"
            subprocess.run(["Rscript", "examples/base_r.R", str(path)],
                           cwd=ROOT, check=True)
            with path.open(newline="") as stream:
                rows = list(csv.DictReader(stream, delimiter="\t"))
            if len(rows) != len(expected) or len({row["metric"] for row in rows}) != len(rows):
                raise ValueError("base R receipt keys")
            compare("base R", {row["metric"]: float(row["value"]) for row in rows}, expected)
    print("BOOK14_PUBLIC_SCIENCE_OK routes=" + ("3" if "--base-r" in sys.argv else "2"))


if __name__ == "__main__":
    main()
