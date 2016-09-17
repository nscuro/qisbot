import sqlite3
import typing

from qisbot.models import ExamData


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
        for schema in self.schemas:
            self.execute(schema)

    def execute(self, query: str) -> sqlite3.Cursor:
        self._connection.execute(query)

    @property
    def schemas(self) -> typing.List[str]:
        """A list of all schemas as SQL create statements."""
        return [self._build_schema('exams', self._map_exam_types())]

    @staticmethod
    def _build_schema(table_name: str, type_generator: typing.Iterable) -> str:
        """Build a table schema.

        Args:
            table_name: Name of the table
            type_generator: Generator for type mappings
        Returns:
            The schema as SQL create statement
        """
        schema = 'CREATE TABLE IF NOT EXISTS {} ('.format(table_name)
        for (name, domain) in type_generator:
            schema += '{} {}, '.format(name, domain)
        last_separator_index = schema.rfind(', ')
        schema = schema[:last_separator_index] + ')'
        return schema

    @staticmethod
    def _map_exam_types() -> typing.Iterable[typing.Tuple[str, str]]:
        """Map the ExamData member types to their equivalent SQL domains.

        Yields:
            The name and SQL domain of a member
        """
        for name, member in ExamData.__members__.items():
            if member.type is int:
                domain = 'INTEGER'
                if name == 'id':
                    domain += ' PRIMARY KEY'
            elif member.type is float:
                domain = 'REAL'
            else:
                domain = 'TEXT'
            yield name, domain

    def __del__(self) -> ():
        """Close the database connection when instance gets garbage collected."""
        self._connection.close()
