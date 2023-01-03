import contextlib
import io

from django.core.management import execute_from_command_line
from django.test import TransactionTestCase


# Tests cannot be run in parallel.
class ManagementCommandTestCase(TransactionTestCase):
    def call_command(self, command):
        err = io.StringIO()
        out = io.StringIO()

        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                execute_from_command_line(command)
            except SystemExit:
                pass

        err.seek(0)
        out.seek(0)

        return tuple(map(str.strip, out.readlines())), tuple(map(str.strip, err.readlines()))
