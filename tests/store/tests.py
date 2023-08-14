import os

from tests.test_case import ManagementCommandTestCase


# Tests cannot be run in parallel.
class StoreTestCase(ManagementCommandTestCase):
    maxDiff = None

    def test_multiple_files_associated_to_latest(self):
        out, err = self.call_command(
            ["manage.py", "makeviewmigration", "store_purchasedproductcalculations", "modify_view"]
        )
        self.assertTupleEqual(err, ())
        self.assertTupleEqual(
            out,
            (
                "",
                "Creating empty migration for the SQL changes.",
                "Migrations for 'store':",
                "tests/store/migrations/0005_modify_view.py",
                "- Raw SQL operation",
                "",
                "Created historical SQL view file - 'view-store_purchasedproductcalculations-0004.sql'.",
                "",
                "Modified migration '0004_add_markup_amount_to_product_calculations' to read from "
                "'view-store_purchasedproductcalculations-0004.sql'.",
                "",
                "Modified migration '0003_create_purchased_product_calculations' to read from "
                "'view-store_purchasedproductcalculations-0004.sql'.",
                "",
                "Modified migration '0005_modify_view' to read from 'view-store_purchasedproductcalculations-"
                "latest.sql' and 'view-store_purchasedproductcalculations-0004.sql'.",
                "",
                "Done - You can now edit 'view-store_purchasedproductcalculations-latest.sql'.",
                "",
            ),
        )
        self.assertTrue(os.path.exists("tests/store/migrations/0005_modify_view.py"))
        self.assertTrue(os.path.exists("tests/store/sql/view-store_purchasedproductcalculations-0004.sql"))

        with open(
            os.path.join("tests", "store", "migrations", "0003_create_purchased_product_calculations.py"),
            "r",
            encoding="utf-8",
        ) as f:
            lines = f.readlines()
        self.assertIn('forward_sql_filename = "view-store_purchasedproductcalculations-0004.sql"\n', lines)

        with open(
            os.path.join("tests", "store", "migrations", "0004_add_markup_amount_to_product_calculations.py"),
            "r",
            encoding="utf-8",
        ) as f:
            lines = f.readlines()
        self.assertIn('sql_filename_which_uses_this_view = "view-store_purchasedproductcalculations-0004.sql"\n', lines)
