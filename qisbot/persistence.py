import enum
import sqlite3
import typing

from qisbot import models


class DatabaseManager(object):
    def __init__(self, database_path: str):
        """Initialize a new DatabaseManager instance.

        Args:
            database_path: Path to the database file to use
        Raises:
            ValueError: When no database path was provided
        """
        if not database_path:
            raise ValueError('database_path must not be None or empty')
        self._connection = sqlite3.connect(database_path)
        for name, schema in self.schemas.items():
            self.execute(schema)

    def execute(self, statement: str, params: typing.Iterable = ()) -> sqlite3.Cursor:
        """Execute a given SQL statement.

        Args:
            statement: The SQL statement to execute
            params: The parameters for the statement
        Returns:
            The cursor for the result
        """
        return self._connection.execute(statement, params)

    def commit(self) -> ():
        """Commits the last actions performed on the database."""
        self._connection.commit()

    @property
    def schemas(self) -> typing.Dict[str, str]:
        """A dict of all table names and schemas as SQL create statements."""
        exams_schema = self._build_schema('exams', models.ExamData)
        return {exams_schema[0]: exams_schema[1]}

    @staticmethod
    def _build_schema(table_name: str, data_model: enum.EnumMeta) -> str:
        """Build a table schema.

        Args:
            table_name: Name of the table
            data_model: Model to build the schema for
        Returns:
            The table name and schema as SQL create statement
        """
        schema = 'CREATE TABLE IF NOT EXISTS {} ('.format(table_name)
        for name, field in data_model.__members__.items():
            if name == 'id':
                domain = 'INTEGER PRIMARY KEY'
            else:
                domain = 'TEXT'
            schema += '{} {}, '.format(name, domain)
        last_separator_index = schema.rfind(', ')
        schema = schema[:last_separator_index] + ')'
        return table_name, schema

    def __del__(self) -> ():
        """Close the database connection when instance gets garbage collected."""
        self._connection.close()
