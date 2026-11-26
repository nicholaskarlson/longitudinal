# Source identity and release boundary

The source is the author's fictional Tonmick college system, **World v1.0.0**, frozen October 4, 2026. Six ordinary observed anchor CSVs have byte identities matching the Book 14 private `source/register.json`. The public paths and their checksums are in `data/SHA256SUMS.txt`. Rows were neither regenerated nor filtered. The public `data/DICTIONARY.csv` is a curated description of their columns, derived from the World dictionary; it does not retain the private root dictionary's other file descriptions, so it has a different hash.

| Path | Rows | Role |
| --- | ---: | --- |
| `data/anchor/participants.csv` | 1,600 | Sampled invitees and design fields |
| `data/anchor/baseline.csv` | 1,219 | Baseline respondents and item records |
| `data/anchor/followup_long.csv` | 3,657 | Three scheduled follow-ups per respondent |
| `data/anchor/registry.csv` | 1,219 | Recorded event time and outcome per respondent |
| `data/anchor/design_colleges.csv` | 40 | College selection and strata |
| `data/anchor/design_joint_pi.csv` | 180 | Joint college inclusion probabilities |

Only paths enumerated in `RELEASE_FILES.json` may enter this public repository. `scripts/check_release.py` rejects an unexpected published path, changed byte, or symlink. A local receipt in the ignored `receipts/` directory is never committed. The positive list intentionally excludes simulator truth, population files, cohort-two records, generator internals, author-only derived records, and every private Book 14 manuscript or production file. No Tonmick private Git history is transferred.

These are synthetic teaching records. The published survey and registry fields are observations within the fictional setting. They cannot substantiate a real-world prevalence, causal effect, or population target. In the worked event calculation, consent withdrawal is treated as censoring; interpretation depends on an assumption that is not checked by the file hash.
