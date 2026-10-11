from django.db.backends.postgresql.base import DatabaseWrapper as PostgreSQLDatabaseWrapper
from django.db.backends.postgresql.features import DatabaseFeatures as PostgreSQLDatabaseFeatures
from django.db.backends.postgresql.operations import DatabaseOperations as PostgreSQLDatabaseOperations


class DatabaseOperations(PostgreSQLDatabaseOperations):
    def deferrable_sql(self):
        # CockroachDB rejects "DEFERRABLE INITIALLY DEFERRED" on foreign keys
        # ("unimplemented: this syntax"), which Django's PostgreSQL backend adds
        # to every FK it creates. Migration 0014 failed on it (2026-10-09).
        return ""


class DatabaseFeatures(PostgreSQLDatabaseFeatures):
    # Constraint checks cannot be deferred to commit time on CockroachDB.
    can_defer_constraint_checks = False


class DatabaseWrapper(PostgreSQLDatabaseWrapper):
    """
    CockroachDB reports PostgreSQL compatibility as 13.x on the wire.
    Django 4.2+ enforces PostgreSQL 14+ for the postgres backend, which blocks
    Cockroach connections despite wire-level compatibility.
    """
    ops_class = DatabaseOperations
    features_class = DatabaseFeatures

    def check_database_version_supported(self) -> None:
        # Intentionally bypass Django's PostgreSQL version gate for CockroachDB.
        return
