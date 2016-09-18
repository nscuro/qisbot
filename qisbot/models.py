import enum
import typing


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
