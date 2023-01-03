import contextlib
import importlib
import io
import os

from django.apps import apps
from django.core.management import BaseCommand
from django.core.management import call_command
from django.db import migrations
from django.db.transaction import atomic


INITIAL_SQL_VIEW_CONTENT = """/*
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
"""

COPIED_SQL_VIEW_CONTENT = """/*
    Commit this file before you make changes to it, so you can look at the commits that follow for a diff.
    You can remove this comment before committing or after, whichever you'd prefer.
    Alter the SQL as needed and then commit the changes.
*/
"""


def create_parser(self, prog_name, subcommand, **kwargs):
    self._called_from_command_line = True
    return BaseCommand._create_parser(self, prog_name, subcommand, **kwargs)


class Command(BaseCommand):
    help = (
        "In the appropriate app, two files will get created. "
        "`sql/view-view_name-0000.sql` - contains the SQL for the view. "
        "`migrations/0000_view_name.py` - a migration that reads the appropriate files in the sql folder. "
        "If the `migrations` and `sql` folder do not exist, they will be created, along with the apps initial "
        "migration, and an empty migration for the view."
    )

    def get_model(self, db_table_name):
        for model in apps.get_models(include_auto_created=True, include_swapped=True):
            if getattr(model._meta, "db_table", "") == db_table_name:
                return model

    def get_choices(self):
        return sorted(
            {
                x._meta.db_table
                for x in apps.get_models(include_auto_created=True, include_swapped=True)
                if getattr(x._meta, "managed", True) == False
            }
        )

    def add_arguments(self, parser):
        choices = self.get_choices()

        parser.add_argument(
            "db_table_name",
            action="store",
            choices=choices,
            help='The view you want to modify".',
        )

        parser.add_argument(
            "migration_name",
            action="store",
            help="The name of the migration that will be created.",
        )

    def call_command(self, *args):
        err = io.StringIO()
        out = io.StringIO()

        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            call_command(*args)

        # Did an error occur?
        if err.tell():
            err.seek(0)
            self.stdout.write(self.style.ERROR(err.read()))
            return False

        # Return the results.
        out.seek(0)
        return out.readlines()

    @atomic
    def handle(self, *args, **options):
        # Get passed in args.
        db_table_name = options["db_table_name"]
        migration_name = options["migration_name"]

        # Get paths we need.
        model = self.get_model(db_table_name)
        model_meta = model._meta
        app_config = model._meta.app_config
        app_label = model_meta.app_label
        path = app_config.path
        sql_path = os.path.join(path, "sql")
        migrations_path = os.path.join(path, "migrations")

        # Does this app have a `migrations` folder?
        has_migrations = True
        if not os.path.exists(migrations_path):
            # No, create one with an __init__.py file.
            os.mkdir(migrations_path)
            with open(os.path.join(migrations_path, "__init__.py"), "w") as f:
                f.write("")
            self.stdout.write(self.style.SUCCESS(f"Created 'migrations' folder in app '{app_label}'."))
            has_migrations = False
        else:  # `migrations` folder exists, but are there any migrations?
            results = self.call_command("showmigrations", app_label)
            if results is False:  # Erred.
                return
            results = map(str.strip, results)
            if "(no migrations)" in results:
                has_migrations = False

        # Does this app have an `sql` folder?
        has_sql_folder = True
        if not os.path.exists(sql_path):
            # No, create one.
            os.mkdir(sql_path)
            self.stdout.write(self.style.SUCCESS(f"Created 'sql' folder in app '{app_label}'."))
            has_sql_folder = False

        if not has_migrations:
            # Create the initial migration for the app.
            self.stdout.write(f"Creating initial migration for app '{app_label}'.")
            results = self.call_command("makemigrations", app_label, "--noinput")
            if not results:  # Erred.
                return
            for result in results:
                self.stdout.write(result)
            self.stdout.write("Creating empty migration for the new SQL view.")
        else:
            self.stdout.write("Creating empty migration for the SQL changes.")

        # Create the empty migration for the SQL view.
        # Force the migration to have a RunSQL operation with text we can easily find/replace.
        migrations.Migration.operations = [
            migrations.RunSQL("SELECT 'replace_forwards';", reverse_sql="SELECT 'replace_reverse';")
        ]
        importlib.invalidate_caches()  # If we don't do this, sometimes we can't import the newly created migration.
        results = self.call_command("makemigrations", app_label, "--empty", f"--name={migration_name}", "--noinput")
        migrations.Migration.operations = []
        if not results:  # Erred.
            return
        for result in results:
            self.stdout.write(result)

        # Get the migration numbers.
        importlib.invalidate_caches()  # If we don't do this, sometimes we can't import the newly created migration.
        results = self.call_command("showmigrations", app_label)
        if not results:  # Erred.
            return

        # Parse the migration numbers that `showmigrations` returns and get the new migration number.
        new_migration_num = 0
        new_migration_name = None
        for line in results:
            num = "".join(filter(str.isdigit, line))
            if num and int(num) > new_migration_num:
                new_migration_num = int(num)
                new_migration_name = line.replace("[X]", "").replace("[ ]", "").strip()

        if new_migration_name is None:
            raise Exception("Unable to find the name of the newly created migration.")

        # Get the highest SQL view filename, so we know what file to use for our reverse in `RunSQL`.
        sql_view_file_num = 2  # With the initial model and our view migration, the minimum this can be is 2.
        has_existing_sql_view_file = False
        if has_sql_folder:
            for filename in os.listdir(sql_path):
                num = "".join(filter(str.isdigit, filename))
                if num:
                    has_existing_sql_view_file = True
                    if int(num) > sql_view_file_num:
                        sql_view_file_num = num

        # Generate the SQL view filenames, so they match the migration numbers.
        # Create the SQL view files, and get some variables for modifying the new empty migration.
        if has_existing_sql_view_file:
            reverse_sql_view_name = f"view-{db_table_name}-{str(sql_view_file_num).zfill(4)}.sql"
            forward_sql_view_name = f"view-{db_table_name}-{str(new_migration_num).zfill(4)}.sql"

            # Create the new version of the SQL view file with the contents of the previous SQL view file.
            with open(os.path.join(sql_path, reverse_sql_view_name), "r", encoding="utf-8") as f_in:
                with open(os.path.join(sql_path, forward_sql_view_name), "w", encoding="utf-8") as f_out:
                    f_out.write(COPIED_SQL_VIEW_CONTENT)
                    f_out.write(f_in.read())
            self.stdout.write(self.style.SUCCESS(f"Created new SQL view file - '{forward_sql_view_name}'."))

            contains_reverse_read = True
            modified_message = (
                f"Modified migration '{new_migration_name}' to read from "
                f"'{forward_sql_view_name}' and '{reverse_sql_view_name}'."
            )
            reverse_text = "reverse_sql"

        else:
            forward_sql_view_name = f"view-{db_table_name}-{str(new_migration_num).zfill(4)}.sql"

            with open(os.path.join(sql_path, forward_sql_view_name), "w", encoding="utf-8") as f:
                f.write(INITIAL_SQL_VIEW_CONTENT)
            self.stdout.write(self.style.SUCCESS(f"Created new SQL view file - '{forward_sql_view_name}'."))

            contains_reverse_read = False
            modified_message = f"Modified migration '{new_migration_name}' to read from '{forward_sql_view_name}'."
            reverse_text = f'"DROP VIEW IF EXISTS {db_table_name};"'

        # Read the migration and add or replace sections with the content needed.
        with open(os.path.join(migrations_path, new_migration_name + ".py"), "r+", encoding="utf-8") as f:
            imports_line_no = 0
            class_line_no = 0
            replace_forwards_line_no = 0
            replace_reverse_line_no = 0
            lines = f.readlines()
            for line_no, line in enumerate(lines):
                if line.find("import") != -1 and not imports_line_no:
                    imports_line_no = line_no
                elif line.startswith("class Migration"):
                    class_line_no = line_no
                elif line.find("replace_forwards") != -1:
                    replace_forwards_line_no = line_no
                elif line.find("replace_reverse") != -1:
                    replace_reverse_line_no = line_no
            lines[replace_reverse_line_no] = lines[replace_reverse_line_no].replace(
                '''"SELECT 'replace_reverse';"''', reverse_text
            )
            lines[replace_forwards_line_no] = lines[replace_forwards_line_no].replace(
                '''"SELECT 'replace_forwards';"''', "forwards_sql"
            )
            lines[class_line_no - 1 : class_line_no] = [
                f'sql_path = "{os.path.relpath(sql_path)}"\n',
                f'forward_sql_view_name = "{forward_sql_view_name}"\n',
                f'reverse_sql_view_name = "{reverse_sql_view_name}"\n' if contains_reverse_read else "",
                "\n",
                'with open(f"{os.path.join(sql_path, forward_sql_view_name)}", mode="r") as f:\n',
                "    forwards_sql = f.read()\n",
                "\n",
                'with open(f"{os.path.join(sql_path, reverse_sql_view_name)}", mode="r") as f:\n'
                if contains_reverse_read
                else "",
                "    reverse_sql = f.read()\n" if contains_reverse_read else "",
                "\n" if contains_reverse_read else "",
            ]
            lines[imports_line_no - 1 : imports_line_no] = [
                "import os\n",
                "\n",
            ]
            f.seek(0)
            f.writelines(lines)
        self.stdout.write(self.style.SUCCESS(modified_message))
        self.stdout.write(f"Done - You can now edit '{forward_sql_view_name}'.")
