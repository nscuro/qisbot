import sqlite3
import typing

from qisbot import models
from qisbot.exceptions import PersistenceException


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

    def execute(self, statement: str, params: typing.Iterable = ()) -> sqlite3.Cursor:
        """Execute a given SQL statement.

        Args:
            statement: The SQL statement to execute
            params: The parameters for the statement
        Returns:
            The cursor for the result
        """
        self._connection.execute(statement, params)

    def commit(self) -> ():
        """Commits the last actions performed on the database."""
        self._connection.commit()

    def insert_exam(self, exam: models.Exam) -> sqlite3.Cursor:
        """Insert a given Exam instance into the database.

        Args:
            exam: The Exam to insert
        Returns:
            The cursor for the result
        Raises:
            PersistenceException: When there is already an exam with the same ID
        """
        statement = 'INSERT INTO exams VALUES ('
        parameters = []
        for name, _ in self._map_exam_types():
            statement += '?, '
            param = getattr(exam, name)
            if isinstance(param, models.ExamStatus):
                param = param.name
            parameters.append(param)
        statement = statement[:statement.rfind(', ')] + ')'
        try:
            result = self.execute(statement, parameters)
        except sqlite3.IntegrityError as err:
            raise PersistenceException('Failed to insert exam') from err
        return result

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
        for name, member in models.ExamData.__members__.items():
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
