"""Independent NumPy route: vectorized scores and exact-time risk accounting."""
import csv
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    with (ROOT / "data" / "anchor" / (name + ".csv")).open(newline="") as stream:
        return list(csv.DictReader(stream))


def calculate():
    people, base, follow, registry = [read(n) for n in
                                      ("participants", "baseline", "followup_long", "registry")]
    ids = np.array([r["student_id"] for r in base])
    offer = np.array([r["offer"] for r in base])
    if len(people) != 1600 or len(base) != 1219 or len(follow) != 3 * len(base):
        raise ValueError("unexpected anchor size")
    if (len(set(ids)) != len(ids) or set(ids) != {r["student_id"] for r in registry}
        or not set(ids) <= {r["student_id"] for r in people}
        or set(offer) != {"0", "1"}):
        raise ValueError("anchor join")
    selected = ids[offer == "0"]
    index = {sid: i for i, sid in enumerate(selected)}
    fidx = {(r["student_id"], r["wave_month"]): r for r in follow}
    if len(fidx) != len(follow) or set(fidx) != {(sid, m) for sid in ids for m in ("3", "6", "12")}:
        raise ValueError("follow-up join")
    bidx = {r["student_id"]: r for r in base}
    scores = np.full((len(selected), 4), np.nan)
    out = {"sampled_invitees": len(people), "baseline_respondents": len(base),
           "unoffered": len(selected)}
    for j, m in enumerate(("0", "3", "6", "12")):
        rows = [bidx[sid] if m == "0" else fidx[(sid, m)] for sid in selected]
        response = np.array([True if m == "0" else r["responded"] == "1" for r in rows])
        if m != "0" and any(r["responded"] not in {"0", "1"} for r in rows):
            raise ValueError("invalid response")
        raw = np.array([[r[f"st{k}"] for k in range(1, 6)] for r in rows])
        if np.any((~response) & np.any(raw != "", axis=1)):
            raise ValueError("unreturned items")
        if np.any((raw != "") & ~np.isin(raw, ["1", "2", "3", "4", "5"])):
            raise ValueError("invalid item")
        values = np.where(raw == "", "0", raw).astype(float)
        values[:, 3] = np.where(raw[:, 3] == "", 0., 6. - values[:, 3])
        valid = (raw != "").sum(axis=1)
        scores[:, j] = np.where(response & (valid >= 4), values.sum(axis=1) / np.maximum(valid, 1), np.nan)
        out[f"returned_{m}"] = int(response.sum())
        out[f"scored_{m}"] = int(np.isfinite(scores[:, j]).sum())
    complete = scores[np.isfinite(scores).all(axis=1)]
    out["four_scored"] = len(complete)
    out["paired_difference"] = float(np.mean(complete[:, 3] - complete[:, 0]))
    kinds = np.array([r["exit_type"] for r in registry])
    time = np.array([float(r["exit_month"]) for r in registry])
    if (set(kinds) != {"none", "withdrawal", "transfer", "consent_withdrawn"}
        or np.any(~np.isfinite(time)) or np.any(time <= 0) or np.any(time > 12)
        or np.any((kinds == "none") != (time == 12.))):
        raise ValueError("invalid registry")
    if any(r["withdrawn_12"] != str(int(r["exit_type"] == "withdrawal")) or
           r["transferred_12"] != str(int(r["exit_type"] == "transfer")) for r in registry):
        raise ValueError("invalid registry flag")
    for k, name in (("withdrawal", "withdrawals_12"), ("transfer", "transfers_12"),
                    ("consent_withdrawn", "consent_censored_12")):
        out[name] = int(np.count_nonzero(kinds == k))
    survival = 1.0
    c_w = c_t = 0.0
    for t in np.unique(time[kinds != "none"]):
        at_risk = int(np.count_nonzero(time >= t))
        w = int(np.count_nonzero((time == t) & (kinds == "withdrawal")))
        tr = int(np.count_nonzero((time == t) & (kinds == "transfer")))
        c_w += survival * w / at_risk
        c_t += survival * tr / at_risk
        survival *= 1 - (w + tr) / at_risk
    out.update(event_free_12=survival, cif_withdrawal_12=c_w, cif_transfer_12=c_t)
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(calculate(), indent=2, sort_keys=True))
