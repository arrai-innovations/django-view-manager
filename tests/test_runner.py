import os
import shutil

# Make sure if tests are run multiple times, that we clean up sql and  migration files/folders for the deleted files.
from django.test.runner import DiscoverRunner


def clean_up_files():
    # We are keeping the employees 0001 migration and __init__.py.
    files_to_delete = (
        "tests/animals/migrations/__init__.py",
        "tests/animals/migrations/0001_initial.py",
        "tests/animals/migrations/0002_create_view.py",
        "tests/animals/sql/view-animals_pets-latest.sql",
        "tests/employees/migrations/0002_create_view.py",
        "tests/employees/migrations/0003_add_date_to_employee_likes.py",
        "tests/employees/sql/view-employees_employeelikes-0002.sql",
        "tests/employees/sql/view-employees_employeelikes-latest.sql",
        "tests/food/migrations/__init__.py",
        "tests/food/migrations/0001_initial.py",
        "tests/food/migrations/0002_create_view.py",
        "tests/food/migrations/0003_change_something.py",
        "tests/food/sql/view-food_sweets-0002.sql",
        "tests/food/sql/view-food_sweets-latest.sql",
    )

    for path in files_to_delete:
        if os.path.exists(path):
            os.remove(path)


def clean_up_folders():
    # We are keeping the animals sql folder and employees migrations folder.
    folders_to_delete = (
        "tests/animals/migrations",
        "tests/employees/sql",
        "tests/food/migrations",
        "tests/food/sql",
    )

    for path in folders_to_delete:
        if os.path.exists(path):
            # Make sure we delete the folder, even if it is not empty.
            shutil.rmtree(path)


class TestRunner(DiscoverRunner):
    parallel = 0
    interactive = False
    verbosity = 2
    shuffle = None
    buffer = True

    def teardown_databases(self, old_config, **kwargs):
        super().teardown_databases(old_config, **kwargs)

        # We do this cleanup, so you can locally run tests.
        clean_up_files()
        clean_up_folders()
