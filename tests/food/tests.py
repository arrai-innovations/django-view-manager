import os
import shutil

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

        # Cleanup - We need to delete these folders for the other tests in this class.
        shutil.rmtree("tests/food/migrations")
        shutil.rmtree("tests/food/sql")

    def test_show_migrations_err_when_creating_initial_migration(self):
        out, err = self.mock_call_command_returning_an_error("showmigrations", 1, "food_sweets", "create_view")
        self.assertTupleEqual(err, ())
        self.assertTupleEqual(
            out,
            (
                "",
                "Created 'migrations' folder in app 'food'.",
                "An error occurred.",
            ),
        )
        self.assertTrue(os.path.exists("tests/food/migrations/__init__.py"))
        self.assertFalse(os.path.exists("tests/food/migrations/0001_initial.py"))
        self.assertFalse(os.path.exists("tests/food/migrations/0002_create_view.py"))
        self.assertFalse(os.path.exists("tests/food/sql/view-food_sweets-latest.sql"))

        # Cleanup - We need to delete these folders for the other tests in this class.
        shutil.rmtree("tests/food/migrations")

    def test_make_migrations_err_when_creating_initial_migration(self):
        out, err = self.mock_call_command_returning_an_error("makemigrations", 1, "food_sweets", "create_view")
        self.assertTupleEqual(err, ())
        self.assertTupleEqual(
            out,
            (
                "",
                "Created 'migrations' folder in app 'food'.",
                "",
                "Creating initial migration for app 'food'.",
                "An error occurred.",
            ),
        )
        self.assertTrue(os.path.exists("tests/food/migrations/__init__.py"))
        self.assertFalse(os.path.exists("tests/food/migrations/0001_initial.py"))
        self.assertFalse(os.path.exists("tests/food/migrations/0002_create_view.py"))
        self.assertFalse(os.path.exists("tests/food/sql/view-food_sweets-latest.sql"))

        # Cleanup - We need to delete these folders for the other tests in this class.
        shutil.rmtree("tests/food/migrations")

    def test_show_migrations_err_when_getting_migration_numbers_and_names(self):
        out, err = self.mock_call_command_returning_an_error("showmigrations", 2, "food_sweets", "create_view")
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
                "An error occurred.",
            ),
        )
        self.assertTrue(os.path.exists("tests/food/migrations/__init__.py"))
        self.assertTrue(os.path.exists("tests/food/migrations/0001_initial.py"))
        self.assertFalse(os.path.exists("tests/food/migrations/0002_create_view.py"))
        self.assertFalse(os.path.exists("tests/food/sql/view-food_sweets-latest.sql"))

        # Cleanup - We need to delete these folders for the other tests in this class.
        shutil.rmtree("tests/food/migrations")
        shutil.rmtree("tests/food/sql")

    def test_make_migrations_err_when_creating_empty_migration(self):
        out, err = self.mock_call_command_returning_an_error("makemigrations", 2, "food_sweets", "create_view")
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
                "An error occurred.",
            ),
        )
        self.assertTrue(os.path.exists("tests/food/migrations/__init__.py"))
        self.assertTrue(os.path.exists("tests/food/migrations/0001_initial.py"))
        self.assertFalse(os.path.exists("tests/food/migrations/0002_create_view.py"))
        self.assertFalse(os.path.exists("tests/food/sql/view-food_sweets-latest.sql"))

        # Cleanup - We need to delete these folders for the other tests in this class.
        shutil.rmtree("tests/food/migrations")
        shutil.rmtree("tests/food/sql")

    def test_show_migrations_err_when_getting_the_new_migration_number_and_name(self):
        with self.assertRaises(RuntimeError):
            _out, _err = self.mock_call_command_returning_an_error("showmigrations", 3, "food_sweets", "create_view")

        self.assertTrue(os.path.exists("tests/food/migrations/__init__.py"))
        self.assertTrue(os.path.exists("tests/food/migrations/0001_initial.py"))
        self.assertTrue(os.path.exists("tests/food/migrations/0002_create_view.py"))
        self.assertFalse(os.path.exists("tests/food/sql/view-food_sweets-latest.sql"))

        # Cleanup - We need to delete these folders for the other tests in this class.
        shutil.rmtree("tests/food/migrations")
        shutil.rmtree("tests/food/sql")
