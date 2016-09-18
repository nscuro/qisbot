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


def map_to_exam(source: typing.Union[html.HtmlElement, typing.Tuple[str]]) -> models.Exam:
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
            if current_cell.text == '&nbsp':
                attribute_value = None
            else:
                attribute_value = current_cell.text_content().strip()
            setattr(exam, name, attribute_value)
        return exam

    def map_from_sql(query_result: typing.Tuple) -> Exam:
        if len(query_result) != len(ExamData.__members__):
            raise ValueError('Unexpected amount of colums (Expected {}, got {})'.format(len(query_result),
                                                                                        len(ExamData.__members__)))
        exam = Exam()
        for name, member in ExamData.__members__.items():
            setattr(exam, name, query_result[member.value])
        return exam

    if isinstance(source, html.HtmlElement):
        return map_from_html(source)
    elif isinstance(source, typing.Tuple[str]):
        return map_from_sql(source)
    else:
        raise TypeError('Cannot map Exam from type {}'.format(str(type(source))))
