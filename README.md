# Longitudinal Reasoning with Statistics — public companion

Open teaching data and independently checkable worked examples for Nicholas Elliott Karlson's developing **Book 14**, *Longitudinal Reasoning with Statistics*, in the NEKpress Research: Proof-First Guides series.

**The book is in development.** This is a versioned companion starter, not a claim that the manuscript or a KDP edition is complete. The Tonmick college system is wholly synthetic. Results here describe the invented records and do not estimate effects in a real population.

## Start here

- [Reader and downloads](https://nicholaskarlson.github.io/longitudinal/) (available once GitHub Pages is enabled).
- [Source provenance and reuse terms](SOURCE.md) and [licenses](LICENSES.md).
- [Column dictionary](data/DICTIONARY.csv), [six frozen CSV files](data/anchor/), and [file hashes](data/SHA256SUMS.txt).
- [Unit map](UNIT_MAP.md) marks which data are available here and which teaching fixtures live elsewhere.

These six CSV files are an exact byte-for-byte public export of the ordinary observed anchor in Tonmick World v1.0.0 and Book 14's registered input. `participants.csv` contains 1,600 invitees; the baseline survey, registry and three follow-ups cover 1,219 respondents. College sampling design and joint inclusion files are included. Blank survey entries remain blank; the companion does not impute them. The public dictionary was selected and adapted from the World dictionary to describe only these six released files.

## Reproduce two examples

From the repository root, with Python 3.10+ and NumPy installed (`python3 -m pip install -r requirements-local.txt`):

```bash
python3 scripts/check_release.py
python3 scripts/verify.py
python3 scripts/verify.py --base-r
```

The final command requires base R. `scripts/verify.py --base-r` executes R and compares all three routes; its temporary receipt is discarded after checking. CI also executes base R. The two examples cover an unoffered-group four-wave stress-score change and an exact-time competing-risk calculation for all baseline respondents. The change is a selected complete-panel description, not a population change or treatment effect. The event curve treats transfer as a competing exit and consent withdrawal as censoring; censoring assumptions and design-aware uncertainty need separate review.

Hash agreement shows source identity. Numerical agreement checks these defined calculations. Neither makes a fictional study empirical or validates causal inference, missingness assumptions, measurement invariance, or transport.

## Use and citation

See [CITATION.cff](CITATION.cff) and [LICENSES.md](LICENSES.md). Data and explanatory text are CC BY 4.0; new analysis and checking code is MIT licensed. Credit the author, the synthetic Tonmick World v1.0.0 source and the specific companion version or commit when reusing the records. This repository does not release World hidden truth, population frames, generator, author-only derived files, private manuscript, or private Git history.

Issues and corrections: [open an issue](https://github.com/nicholaskarlson/longitudinal/issues). Quote the repository commit and the dataset hash when reporting a numerical discrepancy.
