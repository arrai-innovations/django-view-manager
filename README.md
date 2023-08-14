# django-view-manager

A management command for django, designed to provide a way in pull requests, to see a diff of the sql (`CREATE VIEW ...`) for unmanaged models.

Capable of handling migrations with the same number (refer to the musicians app and test) and partially capable of handing views that use other views. Views using views requires some manual additions to migrations, so it can drop required views and set them back up (refer to migration 0004 in the store app for how this can be accomplished). Once set up, it is capable of updating the sql view name in any migration that uses it.

The management command creates an `sql` folder inside an app, along with files like `view-animals_pets-latest.sql` (live) and `view-animals_pets-0002.sql` (historical), where you write your sql. Migrations are also created in the process, which read these files, so you don't need to create them yourself.

Refer to folder and file structure, and usage, for more detailed information.

![Flake8](https://docs.arrai-dev.com/django-view-manager/artifacts/main/flake8.svg)

![Python 3.7 - Django 3.2](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.7%20-%20django%203.2.svg) [![Coverage](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.7%20-%20django%203.2.coverage.svg)](https://docs.arrai-dev.com/django-view-manager/artifacts/main/htmlcov_python%203.7%20-%20django%203.2/)

![Python%203.7%20-%20Django%203.2](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.8%20-%20django%203.2.svg) [![Coverage](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.8%20-%20django%203.2.coverage.svg)](https://docs.arrai-dev.com/django-view-manager/artifacts/main/htmlcov_python%203.8%20-%20django%203.2/)

![Python%203.7%20-%20Django%203.2](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.8%20-%20django%204.0.svg) [![Coverage](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.8%20-%20django%204.0.coverage.svg)](https://docs.arrai-dev.com/django-view-manager/artifacts/main/htmlcov_python%203.8%20-%20django%204.0/)

![Python%203.7%20-%20Django%203.2](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.8%20-%20django%204.1.svg) [![Coverage](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.8%20-%20django%204.1.coverage.svg)](https://docs.arrai-dev.com/django-view-manager/artifacts/main/htmlcov_python%203.8%20-%20django%204.1/)

![Python%203.7%20-%20Django%203.2](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.9%20-%20django%203.2.svg) [![Coverage](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.9%20-%20django%203.2.coverage.svg)](https://docs.arrai-dev.com/django-view-manager/artifacts/main/htmlcov_python%203.9%20-%20django%203.2/)

![Python%203.7%20-%20Django%203.2](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.9%20-%20django%204.0.svg) [![Coverage](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.9%20-%20django%204.0.coverage.svg)](https://docs.arrai-dev.com/django-view-manager/artifacts/main/htmlcov_python%203.9%20-%20django%204.0/)

![Python%203.7%20-%20Django%203.2](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.9%20-%20django%204.1.svg) [![Coverage](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.9%20-%20django%204.1.coverage.svg)](https://docs.arrai-dev.com/django-view-manager/artifacts/main/htmlcov_python%203.9%20-%20django%204.1/)

![Python%203.7%20-%20Django%203.2](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.10%20-%20django%203.2.svg) [![Coverage](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.10%20-%20django%203.2.coverage.svg)](https://docs.arrai-dev.com/django-view-manager/artifacts/main/htmlcov_python%203.10%20-%20django%203.2/)

![Python%203.7%20-%20Django%203.2](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.10%20-%20django%204.0.svg) [![Coverage](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.10%20-%20django%204.0.coverage.svg)](https://docs.arrai-dev.com/django-view-manager/artifacts/main/htmlcov_python%203.10%20-%20django%204.0/)

![Python%203.7%20-%20Django%203.2](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.10%20-%20django%204.1.svg) [![Coverage](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.10%20-%20django%204.1.coverage.svg)](https://docs.arrai-dev.com/django-view-manager/artifacts/main/htmlcov_python%203.10%20-%20django%204.1/)

![Python%203.7%20-%20Django%203.2](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.11%20-%20django%204.1.svg) [![Coverage](https://docs.arrai-dev.com/django-view-manager/artifacts/main/python%203.11%20-%20django%204.1.coverage.svg)](https://docs.arrai-dev.com/django-view-manager/artifacts/main/htmlcov_python%203.11%20-%20django%204.1/)

**Table of Contents**

<!-- prettier-ignore-start -->
<!--TOC-->

- [django-view-manager](#django-view-manager)
- [Installation](#installation)
- [Requirements](#requirements)
- [Folder and File Structure](#folder-and-file-structure)
- [Usage](#usage)
  - [Calling the command with no arguments:](#calling-the-command-with-no-arguments)
  - [Calling the command with arguments on a new app:](#calling-the-command-with-arguments-on-a-new-app)
  - [Calling the command again, when changes are needed:](#calling-the-command-again-when-changes-are-needed)

<!--TOC-->
<!-- prettier-ignore-end -->

# Installation

```shell
$ pip install django-view-manager
```

or

```shell
$ pipenv install django-view-manager
```

Add `django-view-manager.utils` to the INSTALLED_APPS in settings. If possible, do this in your development settings only, as you don't need this package on a production server.

```python
INSTALLED_APPS = [
    ...
    "django-view-manager.utils",
    ...
]
```

# Requirements

At least a django 3.2 and python 3.7.

It may work in an older django, but we only test against supported versions.

# Folder and File Structure

The following folder and file structure is used by this management command. If you were to run the commands listed under usage, you would end up with the following:

```shell
project_name
    employees
        migrations
            0001_initial.py
            0002_create_view.py
            0003_add_date_to_employee_likes.py
        sql
            view-employees_employeelikes-0002.sql
            view-employees_employeelikes-latest.sql
        __init__.py
        apps.py
        models.py
```

The numbers in a filename are associated to the corresponding migration number, and are meant to be historic.

# Usage

If you need to know how to run a django management command, please refer to the documentation in django for more details.

Examples in this documentation use the apps in the test folder, which are also used by tests. The examples will focus on the `employees` app.

https://github.com/arrai-innovations/django-view-manager/blob/ccf70282f4ca5a45946a514fd859b8352706296a/tests/employees/models.py#L4-L27

## Calling the command with no arguments:

```shell
$ python manage.py makeviewmigration
```

The results will be:

```shell
$ python manage.py makeviewmigration [-h] [--version] [-v {0,1,2,3}] [--settings SETTINGS] [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color]
                                     [--skip-checks]
                                     {animals_pets,employees_employeelikes,food_sweets} migration_name
manage.py makeviewmigration: error: the following arguments are required: db_table_name, migration_name
```

## Calling the command with arguments on a new app:

```shell
$ python manage.py makeviewmigration employees_employeelikes create_view
```

The results will be:

```
Created 'migrations' folder in app 'employees'.
‧
Creating initial migration for app 'employees'.
Migrations for 'employees':
  project_name/employees/migrations/0001_initial.py
    - Create model Sweets
‧
Created 'sql' folder in app 'employees'.
‧
Creating empty migration for the new SQL view.
Migrations for 'employees':
  project_name/employees/migrations/0002_create_view.py
    - Raw SQL operation
‧
Created new SQL view file - 'view-employees_employeelikes-latest.sql'.
‧
Modified migration '0002_create_view' to read from 'view-employees_employeelikes-latest.sql'.
‧
Done - You can now edit 'view-employees_employeelikes-latest.sql'.
```

Instructions will be added into the `view-employees_employeelikes-latest.sql` file:

```sql
/*
    This file was generated using django-view-manager 1.0.0.
    Add the SQL for this view and then commit the changes.
    You can remove this comment before committing.
‧
    When you have changes to make to this sql, you need to run the makeviewmigration command
    before altering the sql, so the historical sql file is created with the correct contents.
‧
    eg.
    DROP VIEW IF EXISTS animals_pets;
    CREATE VIEW
        animals_pets AS
    SELECT
        1 AS id,
        42 AS employee_id,
        'Kittens' AS name
    UNION
        2 AS id,
        314 AS employee_id,
        'Puppies' AS name
*/
```

## Calling the command again, when changes are needed:

<b>Important:</b> Run the command before you alter the contents of your sql file, like `view-employees_employeelikes-latest.sql`. If you do not, the historical version created by the command will not contain the sql that it should,

```shell
$ python manage.py makeviewmigration employees_employeelikes add_date_to_employee_likes
```

The results will be:

```
Creating empty migration for the SQL changes.
Migrations for 'employees':
  tests/employees/migrations/0003_add_date_to_employee_likes.py
    - Raw SQL operation
‧
Created historical SQL view file - 'view-employees_employeelikes-0002.sql'.
‧
Modified migration '0002_create_view' to read from 'view-employees_employeelikes-0002.sql'.
‧
Modified migration '0003_add_date_to_employee_likes' to read from 'view-employees_employeelikes-latest.sql' and 'view-employees_employeelikes-0002.sql'.
‧
Done - You can now edit 'view-employees_employeelikes-latest.sql'.
```

The historic file `view-employees_employeelikes-0002.sql` becomes a copy of `view-employees_employeelikes-latest.sql`, and the corresponding migration 0002 is modified to use this historic file.

```sql
/*
    This file was generated using django-view-manager 1.0.0.
    Modify the SQL for this view and then commit the changes.
    You can remove this comment before committing.
‧
    When you have changes to make to this sql, you need to run the makeviewmigration command
    before altering the sql, so the historical sql file is created with the correct contents.
*/
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
```
