import os

from tests.test_case import ManagementCommandTestCase


# Tests cannot be run in parallel.
class StoreTestCase(ManagementCommandTestCase):
    maxDiff = None

    def test_migrations_with_the_same_number(self):
        out, err = self.call_command(["manage.py", "makeviewmigration", "band_info", "add_album_count"])

        self.assertTupleEqual(err, ())
        self.assertTupleEqual(
            out,
            (
                "",
                "Creating empty migration for the SQL changes.",
                "Migrations for 'musicians':",
                "tests/musicians/migrations/0005_add_album_count.py",
                "- Raw SQL operation",
                "",
                "Created historical SQL view file - 'view-band_info-0003-add_founded_date.sql'.",
                "",
                "Modified migration '0003_add_founded_date' to read from 'view-band_info-0003-add_founded_date.sql'.",
                "",
                "Modified migration '0005_add_album_count' to read from"
                " 'view-band_info-latest.sql' and 'view-band_info-0003-add_founded_date.sql'.",
                "",
                "Done - You can now edit 'view-band_info-latest.sql'.",
                "",
            ),
        )
        self.assertTrue(os.path.exists("tests/musicians/migrations/0005_add_album_count.py"))
        self.assertTrue(os.path.exists("tests/musicians/sql/view-band_info-0003-add_founded_date.sql"))

        with open(
            os.path.join("tests", "musicians", "migrations", "0003_add_founded_date.py"),
            "r",
            encoding="utf-8",
        ) as f:
            lines = f.readlines()
        self.assertIn('forward_sql_filename = "view-band_info-0003-add_founded_date.sql"\n', lines)

        with open(
            os.path.join("tests", "musicians", "migrations", "0005_add_album_count.py"),
            "r",
            encoding="utf-8",
        ) as f:
            lines = f.readlines()
        self.assertIn('reverse_sql_filename = "view-band_info-0003-add_founded_date.sql"\n', lines)
        self.assertIn('forward_sql_filename = "view-band_info-latest.sql"\n', lines)

        # Make another view migration, so we can test that it parses the sql view filename correctly.
        out, err = self.call_command(["manage.py", "makeviewmigration", "band_info", "add_member_list"])
        self.assertTupleEqual(err, ())
        self.assertTupleEqual(
            out,
            (
                "",
                "Creating empty migration for the SQL changes.",
                "Migrations for 'musicians':",
                "tests/musicians/migrations/0006_add_member_list.py",
                "- Raw SQL operation",
                "",
                "Created historical SQL view file - 'view-band_info-0005.sql'.",
                "",
                "Modified migration '0005_add_album_count' to read from 'view-band_info-0005.sql'.",
                "",
                "Modified migration '0006_add_member_list' to read from"
                " 'view-band_info-latest.sql' and 'view-band_info-0005.sql'.",
                "",
                "Done - You can now edit 'view-band_info-latest.sql'.",
                "",
            ),
        )
        self.assertTrue(os.path.exists("tests/musicians/migrations/0006_add_member_list.py"))
        self.assertTrue(os.path.exists("tests/musicians/sql/view-band_info-0005.sql"))

        with open(
            os.path.join("tests", "musicians", "migrations", "0005_add_album_count.py"),
            "r",
            encoding="utf-8",
        ) as f:
            lines = f.readlines()
        self.assertIn('forward_sql_filename = "view-band_info-0005.sql"\n', lines)

        with open(
            os.path.join("tests", "musicians", "migrations", "0006_add_member_list.py"),
            "r",
            encoding="utf-8",
        ) as f:
            lines = f.readlines()
        self.assertIn('reverse_sql_filename = "view-band_info-0005.sql"\n', lines)
