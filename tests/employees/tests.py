import os

from tests.test_case import ManagementCommandTestCase


# Tests cannot be run in parallel.
class EmployeesTestCase(ManagementCommandTestCase):
    def test_no_args(self):
        out, err = self.call_command(["manage.py", "makeviewmigration"])
        self.assertIn(
            "manage.py makeviewmigration: error: the following arguments are required: db_table_name, migration_name",
            err,
        )
        self.assertIn("{animals_pets,employees_employeelikes,food_sweets} migration_name", err)

    def test_no_sql_folder(self):
        out, err = self.call_command(["manage.py", "makeviewmigration", "employees_employeelikes", "create_view"])
        self.assertTupleEqual(err, ())
        self.assertTupleEqual(
            out,
            (
                "Created 'sql' folder in app 'employees'.",
                "Creating empty migration for the SQL changes.",
                "Migrations for 'employees':",
                "tests/employees/migrations/0002_create_view.py",
                "- Raw SQL operation",
                "Created new SQL view file - 'view-employees_employeelikes-0002.sql'.",
                "Modified migration '0002_create_view' to read from 'view-employees_employeelikes-0002.sql'.",
                "Done - You can now edit 'view-employees_employeelikes-0002.sql'.",
            ),
        )
        self.assertTrue(os.path.exists("tests/employees/migrations/__init__.py"))
        self.assertTrue(os.path.exists("tests/employees/migrations/0001_initial.py"))
        self.assertTrue(os.path.exists("tests/employees/migrations/0002_create_view.py"))
        self.assertTrue(os.path.exists("tests/employees/sql/view-employees_employeelikes-0002.sql"))

        with open("tests/employees/sql/view-employees_employeelikes-0002.sql", "r") as F:
            content = F.read()
        self.assertEqual(
            content,
            """/*
    Commit this file before you make changes to it, so you can look at the commits that follow for a diff.
    You can remove this comment before committing or after, whichever you'd prefer.
    Add the SQL for this view and then commit the changes.

    eg.
    DROP VIEW IF EXISTS employees_employeelikes;
    CREATE VIEW
        employees_employeelikes AS
    SELECT
        1 AS id,
        42 AS employee_id,
        'Kittens' AS name
    UNION
        2 AS id,
        314 AS employee_id,
        'Puppies' AS name
*/
""",
        )

        # Also test creating a second view.  The contents from the first should be copied to the new view file.
        with open("tests/employees/sql/view-employees_employeelikes-0002.sql", "w") as F:
            F.write(
                "SELECT 1 AS id, 42 AS employee_id, 'Kittens' AS name "
                "UNION 2 AS id, 314 AS employee_id, 'Puppies' AS name;\n"
            )

        out, err = self.call_command(
            ["manage.py", "makeviewmigration", "employees_employeelikes", "add_date_to_employee_likes"]
        )
        self.assertTupleEqual(err, ())
        self.assertTupleEqual(
            out,
            (
                "Creating empty migration for the SQL changes.",
                "Migrations for 'employees':",
                "tests/employees/migrations/0003_add_date_to_employee_likes.py",
                "- Raw SQL operation",
                "Created new SQL view file - 'view-employees_employeelikes-0003.sql'.",
                "Modified migration '0003_add_date_to_employee_likes' to read from "  # No comma here
                "'view-employees_employeelikes-0003.sql' and 'view-employees_employeelikes-0002.sql'.",
                "Done - You can now edit 'view-employees_employeelikes-0003.sql'.",
            ),
        )
        self.assertTrue(os.path.exists("tests/employees/migrations/0003_add_date_to_employee_likes.py"))
        self.assertTrue(os.path.exists("tests/employees/sql/view-employees_employeelikes-0003.sql"))
        with open("tests/employees/sql/view-employees_employeelikes-0003.sql", "r") as F:
            content = F.read()
        self.assertEqual(
            content,
            """/*
    Commit this file before you make changes to it, so you can look at the commits that follow for a diff.
    You can remove this comment before committing or after, whichever you'd prefer.
    Alter the SQL as needed and then commit the changes.
*/
SELECT 1 AS id, 42 AS employee_id, 'Kittens' AS name UNION 2 AS id, 314 AS employee_id, 'Puppies' AS name;
""",
        )
