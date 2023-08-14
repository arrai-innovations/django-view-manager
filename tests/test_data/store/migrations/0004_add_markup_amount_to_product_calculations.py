# Generated by Django 3.2.17 on 2023-08-09 15:10
# Modified using django-view-manager 1.0.4.  Please do not delete this comment.
import os

from django.db import migrations

sql_path = "tests/store/sql"
forward_sql_filename = "view-store_productcalculations-latest.sql"
reverse_sql_filename = "view-store_productcalculations-0002.sql"
sql_filename_which_uses_this_view = "view-store_purchasedproductcalculations-latest.sql"

with open(os.path.join(sql_path, forward_sql_filename), mode="r") as f:
    forwards_sql = f.read()

with open(os.path.join(sql_path, reverse_sql_filename), mode="r") as f:
    reverse_sql = f.read()

with open(os.path.join(sql_path, sql_filename_which_uses_this_view), mode="r") as f:
    sql_which_uses_this_view = f.read()


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0003_create_purchased_product_calculations"),
    ]

    operations = [
        migrations.RunSQL(
            sql=forwards_sql,
            reverse_sql=reverse_sql,
        ),
        # We need to set back up the view that was dropped.
        migrations.RunSQL(
            sql=sql_which_uses_this_view,
            reverse_sql=sql_which_uses_this_view,
        ),
    ]
