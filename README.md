# Ontario Builds infrastructure projects: dashboard and briefing note

Where are Ontario's published infrastructure projects, what stage are they at, and where is the reported budget concentrated? This project cleans the Ontario government's public project list, summarizes it in SQL, and presents it as a Tableau Public dashboard and a one-page briefing note.

## Findings

- The 12 June 2026 file lists **5,935 projects** in 7 categories. **3,930** publish a budget, totalling **$163.8 billion**; **2,005 (34%)** publish none.
- **Transit** is **10%** of projects but **72%** of the reported budget ($117.8 billion).
- The **10 largest projects** hold **71.5%** of the reported budget.
- The **Central** region has **30%** of projects and **88%** of the reported budget.
- **93** projects still marked Planning or Under construction have a target completion year before 2026.

Interactive dashboard: [Ontario Builds Infrastructure Projects on Tableau Public](https://public.tableau.com/app/profile/mincheng.li/viz/OntarioBuildsInfrastructureProjects)

See [reports/briefing_note.md](reports/briefing_note.md) for the one-page summary and its limits.

## Run

Python 3.10 or newer, standard library only.

```bash
python3 build.py
python3 -m unittest -v
```

`build.py` reads the raw CSV, writes `data/projects_clean.csv` (the Tableau input), loads `ontario_builds.db`, runs the six queries in `sql/report_queries.sql`, and writes their results and `reports/summary.json`.

## Cleaning decisions

| Issue in the source | Rows | Decision |
|---|---|---|
| Budget recorded as `0` | 2,005 | Treated as not reported (empty), not as a $0 project |
| Completion date in mixed formats (`27-Mar`, `Sep-34`, `2026`, `March 2027`) | 5,706 | Reduced to a completion year; 1 unclear value (`Jan-80`) left empty |
| Completion date `To Be Determined` | 229 | Year left empty |
| Region blank or `TBD` | 626 | Labelled `Province-wide / not assigned` |
| Status blank | 22 | Labelled `Not reported` |
| Several coordinates in one cell, separated by `\|` | 19 | First point kept for mapping, row flagged `multi-point` |
| Coordinates missing | 417 | Left empty; these projects do not appear on the map |
| Leading or trailing spaces | 1,127 cells | Trimmed |

No rows are dropped: the clean file has the same 5,935 rows as the source.

## Limits

- This is a list of projects the province chose to publish, not all infrastructure spending.
- Budgets are estimated totals over a project's life, not money spent to date, and a third of projects publish none. Category and region totals are therefore lower bounds, and comparisons between categories with very different budget coverage (98% for child care, 20% for recreation) are unreliable.
- Region totals are not adjusted for population.

## Data source

[Ontario Builds: key infrastructure projects](https://data.ontario.ca/dataset/ontario-builds-key-infrastructure-projects), Ontario Data Catalogue, file `ontbuilds-all-20260612.csv`. Contains information licensed under the Open Government Licence – Ontario. This independent analysis is not endorsed by the Government of Ontario.
