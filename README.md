# django-view-manager

A management command for django that provides a semi-automated way to have diffs of sql views.
The SQL of a view is stored in a file and read into a generated migration.

If you create and modify views in migrations, this management command can help automate the creation of migrations that read in files containing SQL views. New versions are created with each use of the management command, so you can diff SQL files, or view diffs in your commits, providing you commit the new file before making changes.

<!-- prettier-ignore-start -->
<!--TOC-->

- [django-view-manager](#django-view-manager)
  - [Installation](#installation)
  - [Requirements](#requirements)
  - [Folder and File Structure](#folder-and-file-structure)
  - [Usage](#usage)

<!--TOC-->
<!-- prettier-ignore-end -->

## Installation

```shell
$ pip install django-view-manager
```

or

```shell
$ pipenv install django-view-manager
```

## Requirements

A `Pipfile` and `dev_requirements.txt` exist. You can choose which you want to use.

At least a django 3.2 and python 3.6 (due to formatted string literals - f-strings).

It may work in an older django, but hasn't been tested with them.

## Folder and File Structure

The following folder and file structure is used by this management command. If you were to run the commands listed under usage, you would end up with the following:

<style>
folder {color: #3B78FF;}
</style>

<pre>
<folder>project_name</folder>
    <folder>employees</folder>
        <folder>migrations</folder>
            0001_initial.py
            0002_create_view.py
            0003_add_date_to_employee_likes.py
        <folder>sql</folder>
            view-employees_employeelikes-0002.sql
            view-employees_employeelikes-0003.sql
        __init__.py
        apps.py
        models.py
</pre>

The numbers in the sql filenames are associated to the corresponding numbers in the migrations.

## Usage

<style>
green {color: #16C60C;}
</style>

If you need to know how to run a django management command, please refer to the documentation in django for more details.

Examples in this documentation use an `employees` app with the following model:

```python
class EmployeeLikes(models.Model):
    employee = models.ForeignKey("employees.Employee", on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=1024)

    class Meta:
        managed = False
        db_table = "employees_employeelikes"
        ordering = ("-name",)
        default_related_name = "likes"

    def __str__(self):
        return f"{self.employee} likes {self.name}."
```

Calling the command with no arguments:

```shell
$ python manage.py makeviewmigration
```

The results will be:

<pre>
usage: manage.py makeviewmigration [-h] [--version] [-v {0,1,2,3}] [--settings SETTINGS] [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color]
                                   [--skip-checks]
                                   {employees_employeelikes}
                                   migration_name
manage.py makeviewmigration: error: the following arguments are required: db_table_name, migration_name
</pre>

Calling the command with arguments on a new app:

```shell
$ python manage.py makeviewmigration employees_employeelikes create_view
```

The results will be:

<pre>
<green>Created 'migrations' folder in app 'employees'.</green>
<green>Created 'sql' folder in app 'employees'.</green>
Creating initial migration for app 'employees'.
Migrations for 'employees':
  project_name/employees/migrations/0001_initial.py
    - Create model EmployeeLikes
Creating empty migration for the new SQL view.
Migrations for 'employees':
  project_name/employees/migrations/0002_create_view.py
    - Raw SQL operation
<green>Created new SQL view file - 'view-employees_employeelikes-0002.sql'.</green>
<green>Modified migration '0002_create_view' to read from 'view-employees_employeelikes-0002.sql'.</green>
Done - You can now edit 'view-employees_employeelikes-0002.sql'.
</pre>

Instructions will be added into the `view-employees_employeelikes-0002.sql` file:

```sql
/*
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
```

Calling the command again, when changes are needed:

```shell
$ python manage.py makeviewmigration employees_employeelikes add_date_to_employee_likes
```

The results will be:

<pre>
Creating empty migration for the SQL changes.
Migrations for 'employees':
  project_name/employees/migrations/0003_add_date_to_employee_likes.py
    - Raw SQL operation
<green>Created new SQL view file - 'view-employees_employeelikes-0003.sql'.</green>
<green>Modified migration '0003_create_view' to read from 'view-employees_employeelikes-0003.sql' and 'view-employees_employeelikes-0002.sql'.</green>
Done - You can now edit 'view-employees_employeelikes-0003.sql'.
</pre>

Instructions will be added into `view-employees_employeelikes-0003.sql`, followed by the contents from `view-employees_employeelikes-0002.sql`. Here we assume that the example from the comment in `view-employees_employeelikes-0002.sql` became the SQL in the file before we did this command.

```sql
/*
    Commit this file before you make changes to it, so you can look at the commits that follow for a diff.
    You can remove this comment before committing or after, whichever you'd prefer.
    Alter the SQL as needed and then commit the changes.
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
