"""Independent, standard-library worked examples on the public ordinary anchor."""
import csv
from collections import Counter, defaultdict
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    with (ROOT / "data" / "anchor" / (name + ".csv")).open(newline="") as stream:
        return list(csv.DictReader(stream))


def score(row):
    items = []
    for number in range(1, 6):
        raw = row[f"st{number}"]
        if raw:
            if raw not in {"1", "2", "3", "4", "5"}:
                raise ValueError("unexpected stress item")
            value = int(raw)
            items.append(6 - value if number == 4 else value)
    return Fraction(sum(items), len(items)) if len(items) >= 4 else None


def calculate():
    people, base, follow, registry = (read(name) for name in
                                      ("participants", "baseline", "followup_long", "registry"))
    people_ids = [r["student_id"] for r in people]
    base_ids = [r["student_id"] for r in base]
    registry_ids = [r["student_id"] for r in registry]
    if (len(people_ids) != 1600 or len(base_ids) != 1219 or
        len(set(people_ids)) != len(people_ids) or
        len(set(base_ids)) != len(base_ids) or
        set(base_ids) != set(registry_ids) or
        len(set(registry_ids)) != len(registry_ids) or
        not set(base_ids) <= set(people_ids)):
        raise ValueError("participant, respondent or registry key mismatch")
    base_by = {r["student_id"]: r for r in base}
    follow_by = {(r["student_id"], r["wave_month"]): r for r in follow}
    if len(follow) != 3657 or len(follow_by) != len(follow) or set(follow_by) != {
        (sid, month) for sid in base_ids for month in ("3", "6", "12")
    }:
        raise ValueError("follow-up keys or waves")
    unoffered = [sid for sid in base_ids if base_by[sid]["offer"] == "0"]
    if len(unoffered) + sum(r["offer"] == "1" for r in base) != len(base):
        raise ValueError("invalid offer")
    scores = {}
    counts = {}
    for month in ("0", "3", "6", "12"):
        values = {}
        returned = 0
        for sid in unoffered:
            row = base_by[sid] if month == "0" else follow_by[(sid, month)]
            response = "1" if month == "0" else row["responded"]
            if response not in {"0", "1"}:
                raise ValueError("invalid response")
            if response == "0" and any(row[f"st{i}"] for i in range(1, 6)):
                raise ValueError("items on nonreturned form")
            returned += response == "1"
            values[sid] = score(row) if response == "1" else None
        scores[month] = values
        counts[f"returned_{month}"] = returned
        counts[f"scored_{month}"] = sum(v is not None for v in values.values())
    complete = [sid for sid in unoffered if all(scores[m][sid] is not None
                                                for m in ("0", "3", "6", "12"))]
    paired = sum((scores["12"][sid] - scores["0"][sid] for sid in complete), Fraction())
    types = Counter(r["exit_type"] for r in registry)
    if set(types) != {"withdrawal", "transfer", "consent_withdrawn", "none"}:
        raise ValueError("unexpected event type")
    events = defaultdict(Counter)
    for row in registry:
        typ = row["exit_type"]
        time = Decimal(row["exit_month"])
        if not time.is_finite() or not Decimal(0) < time <= Decimal(12):
            raise ValueError("invalid exit month")
        if (typ == "none") != (time == Decimal(12)):
            raise ValueError("administrative time")
        if row["withdrawn_12"] != str(int(typ == "withdrawal")) or row["transferred_12"] != str(int(typ == "transfer")):
            raise ValueError("inconsistent event flag")
        if typ != "none":
            events[time][typ] += 1
    risk = len(registry)
    event_free = 1.0
    withdrawal = transfer = 0.0
    for time in sorted(events):
        event = events[time]
        w, t, c = (event[k] for k in ("withdrawal", "transfer", "consent_withdrawn"))
        if w + t + c > risk:
            raise ValueError("negative risk")
        withdrawal += event_free * w / risk
        transfer += event_free * t / risk
        event_free *= 1 - (w + t) / risk
        risk -= w + t + c
    return {"sampled_invitees": len(people), "baseline_respondents": len(base),
            "unoffered": len(unoffered), "four_scored": len(complete),
            "paired_difference": float(paired / len(complete)), **counts,
            "withdrawals_12": types["withdrawal"], "transfers_12": types["transfer"],
            "consent_censored_12": types["consent_withdrawn"],
            "event_free_12": event_free, "cif_withdrawal_12": withdrawal,
            "cif_transfer_12": transfer}


if __name__ == "__main__":
    import json
    print(json.dumps(calculate(), sort_keys=True, indent=2))
