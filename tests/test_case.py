import contextlib
import importlib
import io
import sys
from unittest import mock

from django.core.management import call_command
from django.core.management import execute_from_command_line
from django.test import TransactionTestCase


# Tests cannot be run in parallel.
class ManagementCommandTestCase(TransactionTestCase):
    def call_command(self, command):
        self.stderr = err = io.StringIO()
        self.stdout = out = io.StringIO()

        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                execute_from_command_line(command)
            except SystemExit:
                pass

        err.seek(0)
        out.seek(0)

        return tuple(map(str.strip, out.readlines())), tuple(map(str.strip, err.readlines()))

    def mock_call_command_returning_an_error(self, command, on_which_call, db_table_name, migration_name):
        """
        Mocking the first call of 'showmigrations' or 'makemigrations' is easy.
        Mocking the second, or third call requires us to keep track of how many times it has been called,
        and we need to run the original call command until we get to the one we want to mock.
        So this function is here to help with that, and keep it in one place.
        """
        self._mock_command_count = 0
        self._mock_command_on_count = on_which_call
        self._mock_command = command

        with mock.patch(
            "django_view_manager.utils.management.commands.makeviewmigration.Command._call_command"
        ) as mocked_call_command:
            mocked_call_command.side_effect = self.do_original_call_command_or_err_on_specific_call
            results = self.call_command(["manage.py", "makeviewmigration", db_table_name, migration_name])

        del self._mock_command_count
        del self._mock_command_on_count
        del self._mock_command
        del self.stdout
        del self.stderr

        return results

    def do_original_call_command_or_err_on_specific_call(self, *args):
        """
        This function replicates the code in the _call_command function
        in the management command, minus writing in the error style.
        It also writes an error when we want it to, instead of calling
        """
        err = io.StringIO()
        out = io.StringIO()

        if args[0] == self._mock_command:
            self._mock_command_count += 1

        # If we are running the correct command to mock, and the count is exactly when we want to call it,
        # then set err and continue with the code as it would in _call_command in the management command,
        # otherwise we run the code as it would have in _call_command in the management command.
        if args[0] == self._mock_command and self._mock_command_count == self._mock_command_on_count:
            err.write("An error occurred.\n")

        else:
            # If we don't do this, sometimes we can't import a newly created migration.
            # Do it here, so we don't need to know which calls require it, and which don't.
            importlib.invalidate_caches()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                call_command(*args)

        # Did an error occur?
        if err.tell():
            err.seek(0)
            self.stdout.write(err.read())
            return False

        # Return the results.
        out.seek(0)
        return out.readlines()

    def mock_django_call_command_writing_an_error(self, *args):
        sys.stderr.write("An error occurred.\n")
