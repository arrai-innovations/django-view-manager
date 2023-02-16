import os

from tests.test_case import ManagementCommandTestCase


# Tests cannot be run in parallel.
class EmployeesTestCase(ManagementCommandTestCase):
    maxDiff = None

    def test_no_args(self):
        out, err = self.call_command(["manage.py", "makeviewmigration"])
        self.assertIn(
            "manage.py makeviewmigration: error: the following arguments are required: db_table_name, migration_name",
            err,
        )
        # Depending on the width of your console, migration_name may be on the
        # same line as the db_table_name, or it may wrap it onto the next line.
        self.assertIn("{animals_pets,employees_employeelikes,food_sweets} migration_name", " ".join(err))

    def test_bad_db_table_name(self):
        out, err = self.call_command(["manage.py", "makeviewmigration", "employees_employeehates", "create_view"])
        self.assertIn(
            "manage.py makeviewmigration: error: argument db_table_name: invalid choice: 'employees_"
            "employeehates' (choose from 'animals_pets', 'employees_employeelikes', 'food_sweets')",
            err,
        )

    def test_no_sql_folder(self):
        out, err = self.call_command(["manage.py", "makeviewmigration", "employees_employeelikes", "create_view"])
        self.assertTupleEqual(err, ())
        self.assertTupleEqual(
            out,
            (
                "",
                "Created 'sql' folder in app 'employees'.",
                "",
                "Creating empty migration for the new SQL view.",
                "Migrations for 'employees':",
                "tests/employees/migrations/0002_create_view.py",
                "- Raw SQL operation",
                "",
                "Created new SQL view file - 'view-employees_employeelikes-latest.sql'.",
                "",
                "Modified migration '0002_create_view' to read from 'view-employees_employeelikes-latest.sql'.",
                "",
                "Done - You can now edit 'view-employees_employeelikes-latest.sql'.",
                "",
            ),
        )
        self.assertTrue(os.path.exists("tests/employees/migrations/__init__.py"))
        self.assertTrue(os.path.exists("tests/employees/migrations/0001_initial.py"))
        self.assertTrue(os.path.exists("tests/employees/migrations/0002_create_view.py"))
        self.assertTrue(os.path.exists("tests/employees/sql/view-employees_employeelikes-latest.sql"))

        with open("VERSION", "r") as f:
            version = f.read().strip()

        with open("tests/employees/sql/view-employees_employeelikes-latest.sql", "r") as f:
            content = f.read()
        self.assertEqual(
            content,
            """/*
    This file was generated using django-view-manager {version}.
    Add the SQL for this view and then commit the changes.
    You can remove this comment before committing.

    When you have changes to make to this sql, you need to run the makeviewmigration command
    before altering the sql, so the historical sql file is created with the correct contents.

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
""".format(
                version=version
            ),
        )

        # Test creating a second view.  The contents from the first should be copied to the new view file.
        with open("tests/employees/sql/view-employees_employeelikes-latest.sql", "w") as f:
            f.write(
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
                "",
                "Creating empty migration for the SQL changes.",
                "Migrations for 'employees':",
                "tests/employees/migrations/0003_add_date_to_employee_likes.py",
                "- Raw SQL operation",
                "",
                "Created historical SQL view file - 'view-employees_employeelikes-0002.sql'.",
                "",
                "Modified migration '0002_create_view' to read from 'view-employees_employeelikes-0002.sql'.",
                "",
                "Modified migration '0003_add_date_to_employee_likes' to read from "  # No comma here
                "'view-employees_employeelikes-latest.sql' and 'view-employees_employeelikes-0002.sql'.",
                "",
                "Done - You can now edit 'view-employees_employeelikes-latest.sql'.",
                "",
            ),
        )
        self.assertTrue(os.path.exists("tests/employees/migrations/0003_add_date_to_employee_likes.py"))
        self.assertTrue(os.path.exists("tests/employees/sql/view-employees_employeelikes-0002.sql"))
        self.assertTrue(os.path.exists("tests/employees/sql/view-employees_employeelikes-latest.sql"))
        with open("tests/employees/sql/view-employees_employeelikes-latest.sql", "r") as f:
            content = f.read()

        self.assertEqual(
            content,
            """/*
    This file was generated using django-view-manager {version}.
    Modify the SQL for this view and then commit the changes.
    You can remove this comment before committing.

    When you have changes to make to this sql, you need to run the makeviewmigration command
    before altering the sql, so the historical sql file is created with the correct contents.
*/
SELECT 1 AS id, 42 AS employee_id, 'Kittens' AS name UNION 2 AS id, 314 AS employee_id, 'Puppies' AS name;
""".format(
                version=version
            ),
        )

        # Test creating a third view.  The contents from the first should be copied to the new view file.
        with open("tests/employees/sql/view-employees_employeelikes-latest.sql", "w") as f:
            f.write(
                (
                    """/*
    This file was generated using django-view-manager {version}.
    Modify the SQL for this view and then commit the changes.
    You can remove this comment before committing.

    When you have changes to make to this sql, you need to run the makeviewmigration command
    before altering the sql, so the historical sql file is created with the correct contents.
*/
SELECT 1 AS id, 42 AS employee_id, 'Kittens' AS name, now() as when """
                    "UNION 2 AS id, 314 AS employee_id, 'Puppies' AS name, now() as when;\n"
                ).format(version=version)
            )

        # Remove the generated line from the 'latest' migration, so we run the code to add it back in.
        with open("tests/employees/migrations/0003_add_date_to_employee_likes.py", "r+") as f:
            lines = f.readlines()
            modified_line_no = 0
            for line_no, line in enumerate(lines):
                if line.find("Modified using django-view-manager") != -1:
                    modified_line_no = line_no
                    break
            # Remove the line
            lines[modified_line_no : modified_line_no + 1] = []
            f.seek(0)
            f.truncate(0)
            f.writelines(lines)

        out, err = self.call_command(
            ["manage.py", "makeviewmigration", "employees_employeelikes", "add_rating_to_employee_likes"]
        )
        self.assertTupleEqual(err, ())

        modified_migration_text = (  # Added here, so we don't go over 120 characters on a line.
            "Modified migration '0003_add_date_to_employee_likes' to read from 'view-employees_employeelikes-0003.sql'."
        )
        self.assertTupleEqual(
            out,
            (
                "",
                "Creating empty migration for the SQL changes.",
                "Migrations for 'employees':",
                "tests/employees/migrations/0004_add_rating_to_employee_likes.py",
                "- Raw SQL operation",
                "",
                "Created historical SQL view file - 'view-employees_employeelikes-0003.sql'.",
                "",
                modified_migration_text,
                "",
                "Modified migration '0004_add_rating_to_employee_likes' to read from "  # No comma here
                "'view-employees_employeelikes-latest.sql' and 'view-employees_employeelikes-0003.sql'.",
                "",
                "Done - You can now edit 'view-employees_employeelikes-latest.sql'.",
                "",
            ),
        )
        self.assertTrue(os.path.exists("tests/employees/migrations/0003_add_date_to_employee_likes.py"))
        self.assertTrue(os.path.exists("tests/employees/migrations/0004_add_rating_to_employee_likes.py"))
        self.assertTrue(os.path.exists("tests/employees/sql/view-employees_employeelikes-0002.sql"))
        self.assertTrue(os.path.exists("tests/employees/sql/view-employees_employeelikes-0003.sql"))
        self.assertTrue(os.path.exists("tests/employees/sql/view-employees_employeelikes-latest.sql"))
        with open("tests/employees/sql/view-employees_employeelikes-latest.sql", "r") as f:
            content = f.read()

        sql = (  # Added here, so we don't go over 120 characters on a line.
            "SELECT 1 AS id, 42 AS employee_id, 'Kittens' AS name, now() as when "
            "UNION 2 AS id, 314 AS employee_id, 'Puppies' AS name, now() as when;"
        )

        self.assertEqual(
            content,
            """/*
    This file was generated using django-view-manager {version}.
    Modify the SQL for this view and then commit the changes.
    You can remove this comment before committing.

    When you have changes to make to this sql, you need to run the makeviewmigration command
    before altering the sql, so the historical sql file is created with the correct contents.
*/
{sql}
""".format(
                version=version, sql=sql
            ),
        )
