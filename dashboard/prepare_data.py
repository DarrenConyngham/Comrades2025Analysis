"""Build the slim data files behind the Comrades 2025 results dashboard.

runners.csv  - one row per entrant, without names or race numbers.
leaders.csv  - the top 10 men and women, with names, for the podium table.
"""
import csv
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "comrades_2025_results.csv"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent

STATUS = {
    "DNF": "Did not finish",
    "DNS": "Did not start",
    "Not started": "Did not start",
    "UOF": "Unofficial finisher",
    "Started": "Started - no result",
}


def seconds(t):
    h, m, s = (int(x) for x in t.split(":"))
    return h * 3600 + m * 60 + s


def country(r):
    # ANA = Authorised Neutral Athlete
    return "Neutral athlete (ANA)" if r["Country"] == "ANA" else r["Country"].replace(" (the)", "")


rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
OUT.mkdir(parents=True, exist_ok=True)

with open(OUT / "runners.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["pos", "status", "gender", "category", "country", "club", "wave",
                "time", "time_s", "net_s", "gen_pos"])
    for r in rows:
        finished = r["Time"][:1].isdigit()
        w.writerow([
            r["Pos"],
            "Finished" if finished else STATUS[r["Time"]],
            r["Gender"],
            r["Category"],
            country(r),
            r["Club"],
            r["Wave"].split(" - ")[0],
            r["Time"] if finished else "",
            seconds(r["Time"]) if finished else "",
            seconds(r["Net Time"]) if finished else "",
            r["Gen Pos"],
        ])

with open(OUT / "leaders.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["gender", "gen_pos", "name", "time", "time_s", "category", "country", "club"])
    for g in ("Male", "Female"):
        top = sorted((r for r in rows if r["Gender"] == g and r["Gen Pos"]),
                     key=lambda r: int(r["Gen Pos"]))[:10]
        for r in top:
            w.writerow([g, r["Gen Pos"], r["Name"], r["Time"], seconds(r["Time"]),
                        r["Category"], country(r), r["Club"]])
