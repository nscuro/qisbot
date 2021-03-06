import enum
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

    def persist_exam(self, exam: models.Exam) -> ():
        """Insert a given Exam instance into the database.

        Args:
            exam: The Exam to persist
        Raises:
            PersistenceException: When the given exam already exists in the database
        """
        statement = 'INSERT INTO exams VALUES ('
        parameters = []
        for attr_name in models.ExamData.__members__.keys():
            statement += '?, '
            parameters.append(exam.attributes.get(attr_name))
        statement = statement[:statement.rfind(', ')] + ')'
        try:
            self.execute(statement, params=parameters)
            self.commit()
        except sqlite3.IntegrityError as err:
            raise PersistenceException('Exam with id {} was already persisted'.format(exam.id)) from err

    def update_exam(self, exam_id: str, changes: typing.Dict[str, str]) -> ():
        """Update a given exam record.

        Args:
            exam_id: ID of the exam to update
            changes: Changes to apply
        """
        statement = 'UPDATE exams SET '
        parameters = []
        for attr_name, new_value in changes.items():
            statement += '{}=?, '.format(attr_name)
            parameters.append(new_value)
        statement = statement[:statement.rfind(', ')] + ' WHERE id = ?'
        parameters.append(exam_id)
        self.execute(statement, params=parameters)

    def fetch_exam(self, exam_id: str) -> typing.Optional[models.Exam]:
        """Fetch an Exam with a given ID from the database.

        Args:
            exam_id: ID of the requested Exam
        Returns:
            The resulting Exam instance or None
        """
        statement = 'SELECT * FROM exams WHERE exams.id = ?'
        result = self.execute(statement, params=(int(exam_id),)).fetchone()
        if not result:
            return None
        return models.map_to_exam(result)

    def fetch_all_exams(self) -> typing.List[models.Exam]:
        """Fetch all exams from the database.

        Returns:
            A list of all persisted exams.
        """
        result = self.execute('SELECT * FROM exams').fetchall()
        if not result:
            return []
        exams = []
        for result_item in result:
            exams.append(models.map_to_exam(result_item))
        return exams

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
