import contextlib
import decimal
import importlib
import io
import os

from django.apps import apps
from django.core.management import BaseCommand
from django.core.management import call_command
from django.db import migrations
from django.db.transaction import atomic


VERSION = "1.0.3"


COPIED_SQL_VIEW_CONTENT = f"""/*
    This file was generated using django-view-manager {VERSION}.
    Modify the SQL for this view and then commit the changes.
    You can remove this comment before committing.

    When you have changes to make to this sql, you need to run the makeviewmigration command
    before altering the sql, so the historical sql file is created with the correct contents.
*/
"""

INITIAL_SQL_VIEW_CONTENT = f"""/*
    This file was generated using django-view-manager {VERSION}.
    Add the SQL for this view and then commit the changes.
    You can remove this comment before committing.

    When you have changes to make to this sql, you need to run the makeviewmigration command
    before altering the sql, so the historical sql file is created with the correct contents.

    eg.
    DROP VIEW IF EXISTS {{view_name}};
    CREATE VIEW
        {{view_name}} AS
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

LATEST_VIEW_NAME = "latest"
LATEST_VIEW_NUMBER = decimal.Decimal("Infinity")

# Add a comment right after the Django generated comment, to help find our modified migrations.
MIGRATION_MODIFIED_COMMENT = f"# Modified using django-view-manager {VERSION}.  Please do not delete this comment.\n"


class Command(BaseCommand):
    help = (  # noqa: A003
        "In the appropriate app, two files will get created. "
        "`sql/view-view_name-0000.sql` - contains the SQL for the view. "
        "`migrations/0000_view_name.py` - a migration that reads the appropriate files in the sql folder. "
        "If the `migrations` and `sql` folder do not exist, they will be created, along with the apps initial "
        "migration, and an empty migration for the view."
    )

    def get_model(self, db_table_name):
        matching_model = None
        for model in apps.get_models(include_auto_created=True, include_swapped=True):
            if getattr(model._meta, "db_table", "") == db_table_name:
                matching_model = model

        return matching_model

    def get_choices(self):
        return sorted(
            {
                x._meta.db_table
                for x in apps.get_models(include_auto_created=True, include_swapped=True)
                if getattr(x._meta, "managed", True) is False
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

    def _call_command(self, *args):
        err = io.StringIO()
        out = io.StringIO()

        # If we don't do this, sometimes we can't import a newly created migration.
        # Do it here, so we don't need to know which calls require it, and which don't.
        importlib.invalidate_caches()
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

    def _create_migration_folder_and_initial_migration_if_needed(self, migrations_path, app_label):
        created_initial_migration = False
        if not os.path.exists(migrations_path):
            # No, create one with an __init__.py file.
            os.mkdir(migrations_path)
            with open(os.path.join(migrations_path, "__init__.py"), "w") as f:
                f.write("")
            self.stdout.write(self.style.SUCCESS(f"\nCreated 'migrations' folder in app '{app_label}'."))

        # Are there any migrations?
        results = self._call_command("showmigrations", app_label)
        if results is False:  # Erred.
            return

        results = map(str.strip, results)
        if "(no migrations)" in results:
            # Create the initial migration for the app.
            self.stdout.write(f"\nCreating initial migration for app '{app_label}'.")
            results = self._call_command("makemigrations", app_label, "--noinput")
            if not results:  # Erred.
                return

            for result in results:
                self.stdout.write(result)
            created_initial_migration = True

        return created_initial_migration

    def _create_sql_folder_if_needed(self, sql_path, app_label):
        created_sql_folder = False
        if not os.path.exists(sql_path):
            # No, create one.
            os.mkdir(sql_path)
            self.stdout.write(self.style.SUCCESS(f"\nCreated 'sql' folder in app '{app_label}'."))
            created_sql_folder = True
        return created_sql_folder

    @staticmethod
    def _parse_migration_number_from_show_migrations(line):
        # Find the first word in the line that only contains numbers.
        # The beginning words should either be '[X]', '[', or ']'.
        for word in line.replace(" ", "_").split("_"):
            if word.isdigit():
                return word

    @staticmethod
    def _is_migration_modified(db_table_name, migrations_path, migration_name, num):
        with open(os.path.join(migrations_path, f"{migration_name}.py"), "r") as f:
            # Did we modify this migration?  Check the first 10 lines for our modified comment.
            found_modified_comment = False
            for migration_line_no, migration_line in enumerate(f.readlines()):
                if migration_line.find("Modified using django-view-manager") != -1:
                    found_modified_comment = True

                if not found_modified_comment and migration_line_no > 20:
                    break

                if (
                    migration_line.find(f"view-{db_table_name}-latest") != -1
                    or migration_line.find(f"view-{db_table_name}-{num}") != -1
                ):
                    return True

        return False

    def _get_migration_numbers_and_names(self, db_table_name, app_label, migrations_path, *, only_latest=False):
        show_migration_results = self._call_command("showmigrations", app_label)
        if not show_migration_results:  # Erred.  The reason will be printed to the console via the command.
            if only_latest:
                return None, None
            return None

        # Parse the migration numbers that `showmigrations` returns
        # and get the migration numbers, or new migration number.
        migration_numbers_and_names = {}
        migration_num = migration_name = None

        for line in show_migration_results:
            num = self._parse_migration_number_from_show_migrations(line)

            if num:
                migration_num = decimal.Decimal(num)
                migration_name = line.replace("[X]", "").replace("[ ]", "").strip()

                # When looking for the latest, we haven't modified the migration yet, so we can't match by comment.
                if not only_latest and self._is_migration_modified(db_table_name, migrations_path, migration_name, num):
                    migration_numbers_and_names[migration_num] = migration_name

        if only_latest:
            # If for some reason we can't find the latest migration.
            return migration_num, migration_name

        return migration_numbers_and_names

    @staticmethod
    def _get_sql_numbers_and_names(sql_path, db_table_name):
        sql_numbers_and_names = {}

        view_name_start = f"view-{db_table_name}-"
        view_name_end = ".sql"

        for filename in os.listdir(sql_path):
            if filename.startswith(view_name_start) and filename.endswith(view_name_end):
                sql_file_num = filename.replace(view_name_start, "").replace(view_name_end, "")

                # Convert the number to an int, so we can max them.
                if sql_file_num == LATEST_VIEW_NAME:
                    sql_numbers_and_names[LATEST_VIEW_NUMBER] = filename

                elif sql_file_num.isdigit():
                    sql_numbers_and_names[decimal.Decimal(sql_file_num)] = filename

        return sql_numbers_and_names

    @staticmethod
    def _get_latest_migration_number_and_name(migration_numbers_and_names, sql_numbers_and_names):
        largest_migration_number = decimal.Decimal(0)
        latest_sql_number = None

        for migration_number in migration_numbers_and_names:
            largest_migration_number = migration_number

        for sql_number in sql_numbers_and_names:
            if sql_number is LATEST_VIEW_NUMBER:
                latest_sql_number = sql_number

        if largest_migration_number and latest_sql_number is not None:
            return largest_migration_number, migration_numbers_and_names[largest_migration_number]

        return None, None

    def _create_empty_migration(self, app_label, migration_name, created_initial_migration, created_sql_folder):
        if created_initial_migration or created_sql_folder:
            self.stdout.write("\nCreating empty migration for the new SQL view.")
        else:
            self.stdout.write("\nCreating empty migration for the SQL changes.")

        # Force the migration to have a RunSQL operation with text we can easily find/replace.
        migrations.Migration.operations = [
            migrations.RunSQL("SELECT 'replace_forwards';", reverse_sql="SELECT 'replace_reverse';")
        ]
        results = self._call_command("makemigrations", app_label, "--empty", f"--name={migration_name}", "--noinput")
        migrations.Migration.operations = []
        if not results:  # Erred.
            return

        for result in results:
            self.stdout.write(result)

        return results

    def _copy_latest_sql_view(self, sql_path, latest_sql_filename, historical_sql_filename):
        with open(os.path.join(sql_path, latest_sql_filename), "r+", encoding="utf-8") as f_in:
            content = f_in.read()
            with open(os.path.join(sql_path, historical_sql_filename), "w", encoding="utf-8") as f_out:
                f_out.write(content)

            if "This file was generated using django-view-manager" not in content:
                f_in.seek(0)
                f_in.truncate()
                f_in.write(COPIED_SQL_VIEW_CONTENT)
                f_in.write(content)

        self.stdout.write(self.style.SUCCESS(f"\nCreated historical SQL view file - '{historical_sql_filename}'."))

    def _create_latest_sql_file(self, sql_path, db_table_name):
        latest_sql_filename = f"view-{db_table_name}-{LATEST_VIEW_NAME}.sql"

        with open(os.path.join(sql_path, latest_sql_filename), "w", encoding="utf-8") as f:
            f.write(INITIAL_SQL_VIEW_CONTENT.format(view_name=db_table_name))

        self.stdout.write(self.style.SUCCESS(f"\nCreated new SQL view file - '{latest_sql_filename}'."))

    def _rewrite_latest_migration(self, migrations_path, migration_name, latest_sql_filename, historical_sql_filename):
        with open(os.path.join(migrations_path, migration_name + ".py"), "r+", encoding="utf-8") as f:
            lines = f.readlines()
            generated_line_no = latest_sql_line_no = 0
            add_modified_message = False
            for line_no, line in enumerate(lines):
                if line.find("Generated by Django") != -1:
                    # Should be the first line, but we shouldn't assume that.
                    generated_line_no = line_no
                    if lines[line_no + 1].find("Modified using django-view-manager") == -1:
                        add_modified_message = True
                elif line.find(latest_sql_filename) != -1:
                    latest_sql_line_no = line_no
            # We write lines starting from the bottom to the top, so our line numbers are correct through the process.
            lines[latest_sql_line_no] = lines[latest_sql_line_no].replace(latest_sql_filename, historical_sql_filename)
            if add_modified_message:
                # Insert the modified comment after the Django generated comment.
                lines[generated_line_no + 1 : generated_line_no + 1] = MIGRATION_MODIFIED_COMMENT
            f.seek(0)
            f.truncate(0)
            f.writelines(lines)

    def _rewrite_migration(
        self,
        migrations_path,
        sql_path,
        db_table_name,
        migration_name,
        forward_sql_filename,
        *,
        reverse_sql_filename=None,
    ):
        with open(os.path.join(migrations_path, migration_name + ".py"), "r+", encoding="utf-8") as f:
            generated_line_no = imports_line_no = class_line_no = replace_forwards_line_no = replace_reverse_line_no = 0
            lines = f.readlines()
            for line_no, line in enumerate(lines):
                if line.find("Generated by Django") != -1:
                    # Should be the first line, but we shouldn't assume that.
                    generated_line_no = line_no
                elif line.find("import") != -1 and not imports_line_no:
                    imports_line_no = line_no
                elif line.startswith("class Migration"):
                    class_line_no = line_no
                elif line.find("replace_forwards") != -1:
                    replace_forwards_line_no = line_no
                elif line.find("replace_reverse") != -1:
                    replace_reverse_line_no = line_no
            # We write lines starting from the bottom to the top, so our line numbers are correct through the process.
            lines[replace_reverse_line_no] = lines[replace_reverse_line_no].replace(
                '''"SELECT 'replace_reverse';"''',
                "reverse_sql" if reverse_sql_filename else f'"DROP VIEW IF EXISTS {db_table_name};"',
            )
            lines[replace_forwards_line_no] = lines[replace_forwards_line_no].replace(
                '''"SELECT 'replace_forwards';"''', "forwards_sql"
            )
            lines[class_line_no - 1 : class_line_no] = [
                f'sql_path = "{os.path.relpath(sql_path)}"\n',
                f'forward_sql_filename = "{forward_sql_filename}"\n',
                f'reverse_sql_filename = "{reverse_sql_filename}"\n' if reverse_sql_filename else "",
                "\n",
                'with open(os.path.join(sql_path, forward_sql_filename), mode="r") as f:\n',
                "    forwards_sql = f.read()\n",
                "\n",
                'with open(os.path.join(sql_path, reverse_sql_filename), mode="r") as f:\n'
                if reverse_sql_filename
                else "",
                "    reverse_sql = f.read()\n" if reverse_sql_filename else "",
                "\n" if reverse_sql_filename else "",
            ]
            lines[imports_line_no - 1 : imports_line_no] = [
                "import os\n",
                "\n",
            ]
            # Insert the generated comment at the top.
            lines[generated_line_no + 1 : generated_line_no + 1] = [MIGRATION_MODIFIED_COMMENT]
            f.seek(0)
            f.writelines(lines)

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

        # Does this app have a `migrations` folder, and if so, any migrations?
        created_initial_migration = self._create_migration_folder_and_initial_migration_if_needed(
            migrations_path, app_label
        )
        if created_initial_migration is None:  # Erred.
            return

        # Does this app have an `sql` folder?
        created_sql_folder = self._create_sql_folder_if_needed(sql_path, app_label)

        # Get the migration numbers and names.
        migration_numbers_and_names = self._get_migration_numbers_and_names(db_table_name, app_label, migrations_path)
        if migration_numbers_and_names is None:  # Erred.
            return

        # Get any existing migrations and sql view names and numbers.
        sql_numbers_and_names = self._get_sql_numbers_and_names(sql_path, db_table_name)

        # Figure out if we have a `latest` sql file and which migration is associates to it.
        latest_migration_number, latest_migration_name = self._get_latest_migration_number_and_name(
            migration_numbers_and_names, sql_numbers_and_names
        )

        # Create the empty migration for the SQL view.
        results = self._create_empty_migration(app_label, migration_name, created_initial_migration, created_sql_folder)
        if results is None:  # Erred
            return

        # Get the new migration number and name.
        new_migration_num, new_migration_name = self._get_migration_numbers_and_names(
            db_table_name, app_label, migrations_path, only_latest=True
        )

        if new_migration_name is None:
            raise RuntimeError("Unable to find the name and number of the newly created migration.")

        # Is there a `latest` SQL view and migration?
        if latest_migration_number is not None and latest_migration_name is not None:
            latest_sql_filename = f"view-{db_table_name}-{LATEST_VIEW_NAME}.sql"
            historical_sql_filename = f"view-{db_table_name}-{str(latest_migration_number).zfill(4)}.sql"

            # Copy the `latest` SQL view to match the latest migration number.
            self._copy_latest_sql_view(sql_path, latest_sql_filename, historical_sql_filename)

            # Update the historical migration to use the new historical sql view filename.
            self._rewrite_latest_migration(
                migrations_path, latest_migration_name, latest_sql_filename, historical_sql_filename
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nModified migration '{latest_migration_name}' to read from '{historical_sql_filename}'."
                )
            )

            # Update the empty migration to use the `latest` sql view filename.
            self._rewrite_migration(
                migrations_path,
                sql_path,
                db_table_name,
                new_migration_name,
                forward_sql_filename=latest_sql_filename,
                reverse_sql_filename=historical_sql_filename,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nModified migration '{new_migration_name}' to read from "
                    f"'{latest_sql_filename}' and '{historical_sql_filename}'."
                )
            )

        else:
            latest_sql_filename = f"view-{db_table_name}-{LATEST_VIEW_NAME}.sql"

            # Create the `latest` SQL view.
            self._create_latest_sql_file(sql_path, db_table_name)

            # Update the emtpy migration to use the `latest` sql view filename.
            self._rewrite_migration(
                migrations_path,
                sql_path,
                db_table_name,
                new_migration_name,
                forward_sql_filename=latest_sql_filename,
            )
            self.stdout.write(
                self.style.SUCCESS(f"\nModified migration '{new_migration_name}' to read from '{latest_sql_filename}'.")
            )

        self.stdout.write(f"\nDone - You can now edit '{latest_sql_filename}'.\n\n")
