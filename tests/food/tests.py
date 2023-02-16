import os

from tests.test_case import ManagementCommandTestCase


# Tests cannot be run in parallel.
class FoodTestCase(ManagementCommandTestCase):
    maxDiff = None

    def test_no_migrations_or_sql_folders(self):
        out, err = self.call_command(["manage.py", "makeviewmigration", "food_sweets", "create_view"])
        self.assertTupleEqual(err, ())
        self.assertTupleEqual(
            out,
            (
                "",
                "Created 'migrations' folder in app 'food'.",
                "",
                "Creating initial migration for app 'food'.",
                "Migrations for 'food':",
                "tests/food/migrations/0001_initial.py",
                "- Create model Sweets",
                "",
                "Created 'sql' folder in app 'food'.",
                "",
                "Creating empty migration for the new SQL view.",
                "Migrations for 'food':",
                "tests/food/migrations/0002_create_view.py",
                "- Raw SQL operation",
                "",
                "Created new SQL view file - 'view-food_sweets-latest.sql'.",
                "",
                "Modified migration '0002_create_view' to read from 'view-food_sweets-latest.sql'.",
                "",
                "Done - You can now edit 'view-food_sweets-latest.sql'.",
                "",
            ),
        )
        self.assertTrue(os.path.exists("tests/food/migrations/__init__.py"))
        self.assertTrue(os.path.exists("tests/food/migrations/0001_initial.py"))
        self.assertTrue(os.path.exists("tests/food/migrations/0002_create_view.py"))
        self.assertTrue(os.path.exists("tests/food/sql/view-food_sweets-latest.sql"))
