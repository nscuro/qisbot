import enum
import typing

from lxml import html


class ExamData(enum.Enum):
    """Defines the data (keys) an Exam instance can hold."""

    id = 0
    name = 1
    special = 2
    ruling = 3
    attempt = 4
    nullify = 5
    semester = 6
    date = 7
    grade = 8
    points = 9
    ects = 10
    status = 11
    recognized = 12


class Exam(object):
    def __init__(self):
        self.id = None  # type: str
        self.name = None  # type: str
        self.special = None  # type: str
        self.ruling = None  # type: str
        self.attempt = None  # type: str
        self.nullify = None  # type: str
        self.semester = None  # type: str
        self.date = None  # type: str
        self.grade = None  # type: str
        self.points = None  # type: str
        self.ects = None  # type: str
        self.status = None  # type: str
        self.recognized = None  # type: str

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
        return '<{} ({})>'.format(self.__class__.__name__, self.attributes)


def map_to_exam(source: typing.Union[html.HtmlElement, typing.Tuple[str]]) -> Exam:
    """Map a given source to an equivalent Exam instance.

    Args:
        source: The source to map from
    Returns:
        The resulting Exam instance
    Raises:
        ValueError: When the source's columns / entries don't match the format defined
            in models.ExamData
        TypeError: When source has an unsupported type
    """

    def map_from_html(table_row: html.HtmlElement) -> Exam:
        row_cells = table_row.xpath('.//td')
        if len(row_cells) != len(ExamData.__members__):
            raise ValueError(
                'Unexpected amount of cells (Expected {}, got {})'.format(len(ExamData.__members__), len(row_cells)))
        exam = Exam()
        for name, member in ExamData.__members__.items():
            current_cell = row_cells[member.value]
            if current_cell.text == '&nbsp' or not len(current_cell.text):
                attribute_value = None
            else:
                attribute_value = current_cell.text_content().strip()
            setattr(exam, name, str(attribute_value) if attribute_value else None)
        return exam

    def map_from_sql(query_result: typing.Tuple[str]) -> Exam:
        if len(query_result) != len(ExamData.__members__):
            raise ValueError('Unexpected amount of colums (Expected {}, got {})'.format(len(query_result),
                                                                                        len(ExamData.__members__)))
        exam = Exam()
        for name, member in ExamData.__members__.items():
            attribute_value = query_result[member.value]
            setattr(exam, name, str(attribute_value) if attribute_value else None)
        return exam

    if isinstance(source, html.HtmlElement):
        return map_from_html(source)
    elif isinstance(source, (tuple, list)):
        return map_from_sql(source)
    else:
        raise TypeError('Cannot map Exam from type {}'.format(str(type(source))))


def compare_exams(old: Exam, new: Exam) -> typing.Dict[str, typing.Tuple[str, str]]:
    """Compare two Exam instances.

    Args:
        old: Exam instance containing "old" data
        new: Exam instance containing "new" data
    Returns:
        A dict containing all changes
    """
    changes = {}
    for attr_name in ExamData.__members__.keys():
        old_val = getattr(old, attr_name)
        new_val = getattr(new, attr_name)
        if new_val != old_val:
            changes[attr_name] = (old_val, new_val)
    return changes
