"""Clean the Ontario Builds project list and load it into SQLite.

Run:  python3 build.py
Reads   data/ontbuilds-all-20260612.csv   (raw download, never edited)
Writes  data/projects_clean.csv           (one row per project, for Tableau)
        ontario_builds.db                 (SQLite table `projects`)
        reports/summary.json              (data-quality counts)
        reports/q*.csv                    (results of sql/report_queries.sql)
"""

import csv
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "ontbuilds-all-20260612.csv"
CLEAN = ROOT / "data" / "projects_clean.csv"
DB = ROOT / "ontario_builds.db"
REPORTS = ROOT / "reports"

# Rough bounding box for Ontario, used to catch mistyped coordinates.
LAT_RANGE = (41.5, 57.0)
LON_RANGE = (-95.5, -74.0)


def parse_year(text):
    """Return the completion year, or None if it is missing or unclear.

    The source column mixes formats: '27-Mar' and 'Sep-34' (month-year
    values that a spreadsheet reformatted), '2026', 'March 2027',
    '2027-03-31', and 'To Be Determined'.
    """
    text = text.strip()
    match = re.fullmatch(r"(\d{1,2})-[A-Za-z]{3}", text)      # 27-Mar
    if match:
        return 2000 + int(match.group(1))
    match = re.fullmatch(r"[A-Za-z]{3}-(\d{2})", text)        # Sep-34
    if match:
        year = 2000 + int(match.group(1))
        return year if year <= 2050 else None                 # 'Jan-80' is unclear
    match = re.search(r"(20\d{2})", text)                     # any 4-digit year
    if match:
        return int(match.group(1))
    return None


def parse_coordinates(lat_text, lon_text):
    """Return (lat, lon, note). Multi-point projects keep their first point."""
    if not lat_text.strip() or not lon_text.strip():
        return None, None, "missing"
    note = "multi-point" if "|" in lat_text or "|" in lon_text else "ok"
    try:
        lat = float(lat_text.split("|")[0])
        lon = float(lon_text.split("|")[0])
    except ValueError:
        return None, None, "invalid"
    if not (LAT_RANGE[0] <= lat <= LAT_RANGE[1] and LON_RANGE[0] <= lon <= LON_RANGE[1]):
        return None, None, "outside Ontario"
    return lat, lon, note


def clean_row(number, raw):
    row = {key: (value or "").strip() for key, value in raw.items()}
    budget = float(row["Estimated Total Budget ($)"] or 0)
    lat, lon, coord_note = parse_coordinates(row["Latitude"], row["Longitude"])
    partners = [name for name in ("Provincial", "Federal", "Municipal", "Other")
                if row[name + " Funding"] == "Yes"]
    return {
        "project_id": number,
        "category": row["Category"],
        "ministry": row["Supporting Ministry"],
        "community": row["Community"] or None,
        "region": row["Region"] if row["Region"] not in ("", "TBD") else "Province-wide / not assigned",
        "project": row["Project"],
        "status": row["Status"] or "Not reported",
        "completion_raw": row["Target Completion Date"],
        "completion_year": parse_year(row["Target Completion Date"]),
        # The source uses 0 when no budget is published; it is not a $0 project.
        "budget": budget if budget > 0 else None,
        "provincial_funding": int("Provincial" in partners),
        "federal_funding": int("Federal" in partners),
        "municipal_funding": int("Municipal" in partners),
        "other_funding": int("Other" in partners),
        "funding_partners": len(partners),
        "latitude": lat,
        "longitude": lon,
        "coordinate_note": coord_note,
    }


def count(rows, test):
    return sum(1 for row in rows if test(row))


def main():
    with open(RAW, encoding="utf-8-sig", newline="") as handle:
        raw_rows = list(csv.DictReader(handle))
    rows = [clean_row(number, raw) for number, raw in enumerate(raw_rows, start=1)]
    columns = list(rows[0].keys())

    with open(CLEAN, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    DB.unlink(missing_ok=True)
    db = sqlite3.connect(DB)
    db.execute(f"CREATE TABLE projects ({', '.join(columns)})")
    db.executemany(
        f"INSERT INTO projects VALUES ({', '.join('?' for _ in columns)})",
        [tuple(row.values()) for row in rows],
    )
    db.commit()

    REPORTS.mkdir(exist_ok=True)
    queries = (ROOT / "sql" / "report_queries.sql").read_text().split(";")
    query_number = 0
    for query in queries:
        if "SELECT" not in query:
            continue
        query_number += 1
        cursor = db.execute(query)
        with open(REPORTS / f"q{query_number}.csv", "w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow([column[0] for column in cursor.description])
            writer.writerows(cursor.fetchall())

    edge_space = sum(1 for raw in raw_rows for value in raw.values() if value != value.strip())
    summary = {
        "source_rows": len(raw_rows),
        "clean_rows": len(rows),
        "cells_with_edge_whitespace_trimmed": edge_space,
        "budget_reported": count(rows, lambda r: r["budget"] is not None),
        "budget_not_reported": count(rows, lambda r: r["budget"] is None),
        "total_reported_budget": sum(r["budget"] or 0 for r in rows),
        "completion_year_parsed": count(rows, lambda r: r["completion_year"] is not None),
        "completion_to_be_determined": count(rows, lambda r: r["completion_raw"] == "To Be Determined"),
        "completion_unclear": count(rows, lambda r: r["completion_year"] is None
                                    and r["completion_raw"] != "To Be Determined"),
        "status_not_reported": count(rows, lambda r: r["status"] == "Not reported"),
        "region_not_assigned": count(rows, lambda r: r["region"].startswith("Province-wide")),
        "coordinates": {note: count(rows, lambda r, n=note: r["coordinate_note"] == n)
                        for note in ("ok", "multi-point", "missing", "invalid", "outside Ontario")},
    }
    (REPORTS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
