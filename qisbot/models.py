import enum
import typing

from lxml import html

from qisbot.selectors import Selectors


class ExamStatus(enum.Enum):
    BE = 'passed'
    NB = 'failed'
    EN = 'finally failed'

    @classmethod
    def by_symbol(cls, symbol: str) -> typing.Optional:
        """Get an ExamStatus instance by symbol (which is equal to the instance's name).

        Args:
            symbol: Status composed of two uppercase letters
        Returns:
            The matching status or None
        """
        for name, member in ExamStatus.__members__.items():
            if name == symbol:
                return member
        return None


class ExamData(enum.Enum):
    """Defines the data (keys) an Exam instance can hold."""

    id = (0, int)
    name = (1, str)
    special = (2, str)
    ruling = (3, int)
    attempt = (4, int)
    nullify = (5, str)
    semester = (6, str)
    date = (7, str)
    grade = (8, float)
    points = (9, str)
    ects = (10, float)
    status = (11, ExamStatus)
    recognized = (12, str)

    @property
    def index(self) -> int:
        return self.value[0]

    @property
    def type(self) -> typing.Any:
        return self.value[1]


class Exam(object):
    @property
    def attributes(self) -> typing.Dict[str, typing.Any]:
        """Get a dictionary of all attributes.

        The keys of the dictionary are a lowercase representation of
        the ExamData enum's member names.
        """
        attrs = {}
        for attr in dir(self):
            if attr.startswith('__') or attr == 'attributes':
                continue
            attrs[attr] = getattr(self, attr)
        return attrs

    def __repr__(self):
        return '{} ({})'.format(self.__class__, self.attributes)


def map_exam(table_row: html.HtmlElement) -> typing.Optional[Exam]:
    """Map a table row from the exams extract to a Exam instance.

    Args:
        table_row: The table row
    Returns:
        A corresponding Exam instance or None if the row does not
        contain any cells.
    Raises:
        TypeError: When table_row is not an HTML element
        TypeError: When casting the type of a cell failed
    """
    if not isinstance(table_row, html.HtmlElement):
        raise TypeError
    row_cells = table_row.xpath(Selectors.EXAMS_EXTRACT_EXAMS_CELLS.value)
    if not len(row_cells):
        return None
    exam = Exam()
    for name, member in ExamData.__members__.items():
        if (member.index + 1) > len(row_cells):
            # This row does not contain the data requested
            setattr(exam, name, None)
            continue
        cell = row_cells[member.index]
        if cell.text != '&nbsp':
            cell_text = row_cells[member.index].text_content().strip()
        else:
            # This cell is basically empty
            cell_text = None
        try:
            if member.type is ExamStatus:
                # We can't just call the constructor here
                cell_value = ExamStatus.by_symbol(cell_text)
            elif member.type in (float, int):
                # Casting a number from None won't work
                if not cell_text:
                    cell_value = None
                else:
                    # float needs a dot as decimal separator
                    cell_value = member.type(cell_text.replace(',', '.'))
            else:
                cell_value = member.type(cell_text)
        except ValueError as err:
            raise TypeError('Cannot convert "{}" of type {} to type {}'.format(
                cell_text, type(cell_text), member.type
            )) from err
        else:
            setattr(exam, name, cell_value)
    return exam
