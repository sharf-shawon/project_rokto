import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Wait for the database to be available.

    Polls the default database connection until it's ready,
    or until a timeout is reached.
    """

    help = "Wait for the database to be available"

    def add_arguments(self, parser):
        parser.add_argument(
            "--timeout",
            type=int,
            default=30,
            help="Maximum time (seconds) to wait for the database",
        )
        parser.add_argument(
            "--interval",
            type=float,
            default=0.5,
            help="Polling interval (seconds) between connection attempts",
        )

    def handle(self, *args, **options):
        timeout = options["timeout"]
        interval = options["interval"]
        db_conn = connections["default"]

        start_time = time.monotonic()
        attempts = 0

        self.stdout.write("Waiting for database...")

        while True:
            elapsed = time.monotonic() - start_time
            if elapsed > timeout:
                msg = f"Database not available after {timeout}s"
                self.stdout.write(
                    self.style.ERROR(
                        f"Database not available after {timeout}s "
                        f"({attempts} attempts)",
                    ),
                )
                raise TimeoutError(msg)

            try:
                db_conn.ensure_connection()
                # Run a simple query to verify the connection works
                with db_conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Database available after {elapsed:.1f}s "
                        f"({attempts} attempts)",
                    ),
                )
            except OperationalError:
                attempts += 1
                time.sleep(interval)
            else:
                return
