import enum


class Selectors(enum.Enum):
    """Holds all non-trivial XPath expressions."""
    LOGIN_ACTION_LINK = '//*[@id="wrapper"]/div[3]/a[2]'
    EXAM_ADMINISTRATION_LINK = '//a[text() = "Prüfungsverwaltung" or text() = "Administration of exams"]'
    EXAMS_EXTRACT_LINK = '//a[text() = "Notenspiegel" or text() = "Exams Extract"]'
    SHOW_ACCOMPLISHMENTS_LINK = '//a[@title = "Leistungen anzeigen"]'
    EXAMS_EXTRACT_EXAMS_TABLE = '//form/table[2]'
    EXAMS_EXTRACT_EXAMS_CELLS = './/*[@class = "tabelle1_alignleft" or @class = "tabelle1_aligncenter" ' \
                                'or @class = "tabelle1_alignright"]'
