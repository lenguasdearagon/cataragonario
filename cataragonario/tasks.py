from django.core.files.storage import default_storage
from django.core.management import call_command
from huey.contrib.djhuey import db_task

from django.core.management.base import CommandError

@db_task()
def run_validator(xlsx_file, log_filename):
    # call_command('importmultivariation', xlsx_file, dry_run=True, no_color=True, verbosity=3, stdout=out)
    with open(log_filename, 'w') as f:
        try:
            call_command('importmultivariation', xlsx_file, no_color=True, verbosity=3, stdout=f, stderr=f)
        except CommandError as e:
            exception_details = getattr(e, 'message', repr(e))
            f.write(exception_details)
