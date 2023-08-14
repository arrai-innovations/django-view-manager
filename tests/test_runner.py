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
        "tests/animals/sql/view-animals_pets-bad.sql",
        "tests/animals/sql/view-animals_pets-latest.sql",
        "tests/employees/migrations/0003_create_view.py",
        "tests/employees/migrations/0004_add_date_to_employee_likes.py",
        "tests/employees/migrations/0005_add_rating_to_employee_likes.py",
        "tests/employees/sql/view-employees_employeelikes-0003.sql",
        "tests/employees/sql/view-employees_employeelikes-0004.sql",
        "tests/employees/sql/view-employees_employeelikes-latest.sql",
        "tests/food/migrations/__init__.py",
        "tests/food/migrations/0001_initial.py",
        "tests/food/migrations/0002_create_view.py",
        "tests/food/migrations/0003_change_something.py",
        "tests/food/sql/view-food_sweets-0002.sql",
        "tests/food/sql/view-food_sweets-latest.sql",
        "tests/store/migrations/0005_modify_view.py",
        "tests/store/sql/view-store_purchasedproductcalculations-0004.sql",
        "tests/musicians/migrations/0005_add_album_count.py",
        "tests/musicians/sql/view-band_info-0003-add_founded_date.sql",
        "tests/musicians/migrations/0006_add_member_list.py",
        "tests/musicians/sql/view-band_info-0005.sql",
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


def replace_files():
    for filename in (
        os.path.join("store", "migrations", "0003_create_purchased_product_calculations.py"),
        os.path.join("store", "migrations", "0004_add_markup_amount_to_product_calculations.py"),
        os.path.join("musicians", "migrations", "0003_add_founded_date.py"),
        os.path.join("musicians", "sql", "view-band_info-latest.sql"),
    ):
        with open(
            os.path.join("tests", "test_data", filename),
            "r",
            encoding="utf-8",
        ) as f_in:
            content = f_in.read()
            with open(
                os.path.join("tests", filename),
                "w",
                encoding="utf-8",
            ) as f_out:
                f_out.write(content)


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
        replace_files()
