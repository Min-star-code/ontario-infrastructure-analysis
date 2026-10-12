"""Run:  python3 -m unittest -v"""

import csv
import sqlite3
import unittest

import build


class ParseYearTests(unittest.TestCase):
    def test_spreadsheet_month_year(self):
        self.assertEqual(build.parse_year("27-Mar"), 2027)
        self.assertEqual(build.parse_year("Sep-34"), 2034)

    def test_other_formats(self):
        self.assertEqual(build.parse_year("2026"), 2026)
        self.assertEqual(build.parse_year("March 2027"), 2027)
        self.assertEqual(build.parse_year("2027-03-31"), 2027)

    def test_unknown_stays_empty(self):
        self.assertIsNone(build.parse_year("To Be Determined"))
        self.assertIsNone(build.parse_year("Jan-80"))


class ParseCoordinatesTests(unittest.TestCase):
    def test_single_point(self):
        self.assertEqual(build.parse_coordinates("43.65", "-79.38"), (43.65, -79.38, "ok"))

    def test_multi_point_keeps_first(self):
        self.assertEqual(build.parse_coordinates("43.6|43.5", "-79.3|-79.4"), (43.6, -79.3, "multi-point"))

    def test_missing_and_out_of_range(self):
        self.assertEqual(build.parse_coordinates("", ""), (None, None, "missing"))
        self.assertEqual(build.parse_coordinates("10.0", "-79.38"), (None, None, "outside Ontario"))


class ReconciliationTests(unittest.TestCase):
    """The Tableau input file and the SQL table must give the same totals."""

    @classmethod
    def setUpClass(cls):
        build.main()
        with open(build.CLEAN, encoding="utf-8", newline="") as handle:
            cls.rows = list(csv.DictReader(handle))
        cls.db = sqlite3.connect(build.DB)

    def test_row_count_matches_source(self):
        with open(build.RAW, encoding="utf-8-sig", newline="") as handle:
            source_rows = sum(1 for _ in csv.DictReader(handle))
        self.assertEqual(len(self.rows), source_rows)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM projects").fetchone()[0], source_rows)

    def test_budget_total_matches(self):
        csv_total = sum(float(row["budget"]) for row in self.rows if row["budget"])
        sql_total = self.db.execute("SELECT SUM(budget) FROM projects").fetchone()[0]
        self.assertAlmostEqual(csv_total, sql_total, places=2)

    def test_unreported_budget_is_empty_not_zero(self):
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM projects WHERE budget = 0").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
