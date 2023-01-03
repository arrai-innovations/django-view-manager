import os

from tests.test_case import ManagementCommandTestCase


# Tests cannot be run in parallel.
class AnimalsTestCase(ManagementCommandTestCase):
    def test_no_migrations_folder(self):
        out, err = self.call_command(["manage.py", "makeviewmigration", "animals_pets", "create_view"])
        self.assertTupleEqual(err, ())
        self.assertTupleEqual(
            out,
            (
                "Created 'migrations' folder in app 'animals'.",
                "Creating initial migration for app 'animals'.",
                "Migrations for 'animals':",
                "tests/animals/migrations/0001_initial.py",
                "- Create model Pets",
                "Creating empty migration for the new SQL view.",
                "Migrations for 'animals':",
                "tests/animals/migrations/0002_create_view.py",
                "- Raw SQL operation",
                "Created new SQL view file - 'view-animals_pets-0002.sql'.",
                "Modified migration '0002_create_view' to read from 'view-animals_pets-0002.sql'.",
                "Done - You can now edit 'view-animals_pets-0002.sql'.",
            ),
        )
        self.assertTrue(os.path.exists("tests/animals/migrations/__init__.py"))
        self.assertTrue(os.path.exists("tests/animals/migrations/0001_initial.py"))
        self.assertTrue(os.path.exists("tests/animals/migrations/0002_create_view.py"))
        self.assertTrue(os.path.exists("tests/animals/sql/view-animals_pets-0002.sql"))
