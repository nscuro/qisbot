import typing
from contextlib import contextmanager

import requests
import requests.cookies
from lxml import html
from lxml.etree import ParseError
from lxml.etree import XPathEvalError, XPathSyntaxError

from qisbot.exceptions import ScraperException
from qisbot.exceptions import NoSuchElementException


class Scraper(object):
    def __init__(self, session: requests.Session = None):
        self.session = session or requests.Session()
        self._current_document = None  # type: html.HtmlElement
        self._current_location = None  # type: str
        self._current_status = None  # type: int
        self.allow_redirects = True

    @contextmanager
    def permit_redirects(self, permit=True):
        """Permit or forbid redirects in a context.

        Args:
            permit: Indicate whether or not to permit redirects
        Yields:
            This Scraper instance
        """
        default_value = self.allow_redirects
        self.allow_redirects = permit
        yield self
        self.allow_redirects = default_value

    def fetch(self, url: str) -> html.HtmlElement:
        """Fetch a web page from a given URL.

        Args:
            url: Target URL to fetch from
        Returns:
            The fetched page as parsed HtmlElement
        Raises:
            ValueError: When no URL was provided
            ScraperException: When requesting the page's source or parsing it failed
        """
        if not url:
            raise ValueError('URL must not be None or empty')
        try:
            response = self.session.get(url, allow_redirects=self.allow_redirects)
            response.raise_for_status()
        except requests.RequestException as ex:
            raise ScraperException from ex
        try:
            document = html.fromstring(response.content)  # type: html.HtmlElement
            document.make_links_absolute(base_url=url, resolve_base_href=True)
        except ParseError as err:
            raise ScraperException from err
        self._current_status = response.status_code
        self._current_document = document
        self._current_location = url
        return document

    def select(self, xpath: str, document: html.HtmlElement = None) -> typing.Union[
        bool, float, str, typing.List[html.HtmlElement]]:
        """Perform a selection on a given HTML document.

        As documented in the lxml API documentation, the result of an XPath query
        varies based on the expression.

        See: http://lxml.de/xpathxslt.html#the-xpath-method

        Args:
            xpath: The XPath expression to use
            document: The document to perform the selection on.
                When None, self.current_document will be used.
        Returns:
            The selections result (see type hints for possible types)
        Raises:
            ValueError: When no XPath expression was provided
            ScraperException: When no document is available or the XPath
                expression is invalid
        """
        if not xpath:
            raise ValueError('No XPath for selection provided')
        if document is None and self._current_document is None:
            raise ScraperException('No document available to perform selection on')
        elif document is None:
            # Implies that self._current_document is not None
            document = self._current_document
        try:
            result = document.xpath(xpath)
        except (XPathEvalError, XPathSyntaxError) as err:
            raise ScraperException(xpath) from err
        return result

    def check(self, xpath: str, document: html.HtmlElement = None) -> bool:
        """Execute a boolean XPath expression and validate the result's type.

        Args:
            xpath: The XPath containing a boolean expression
            document: The document to execute the expression on
        Returns:
            The boolean value of the expression
        Raises:
            ScraperException: When the result of the expression is not a boolean
        """
        result = self.select(xpath, document)
        if not isinstance(result, bool):
            raise ScraperException('Cannot check "{}": Result is not a boolean'.format(xpath)) from TypeError
        return result

    def number(self, xpath: str, document: html.HtmlElement = None) -> float:
        """Execute an XPath expression that returns a number and validate the result's type.

        Args:
            xpath: The XPath to execute
            document: The document to execute the expression on
        Returns:
            The desired number as float
        Raises:
            ScraperException: When the result of the expression is not a number
        """
        result = self.select(xpath, document)
        if not isinstance(result, float):
            raise ScraperException('Result of "{}" is not a number'.format(xpath)) from TypeError
        return result

    def text(self, xpath: str, document: html.HtmlElement = None) -> typing.List[str]:
        """Execute an XPath expression that returns a (list of) string and validate the result's type.

        Args:
            xpath:
            document:
        Returns:
            A list of all strings matching the expression. Empty when no match found.
        Raises:
            ScraperException: When the result of the expression is not a list of strings
        """
        result = self.select(xpath, document)
        if isinstance(result, list):
            if not len(result):
                return []
            elif not isinstance(result[0], str):
                # Result has to be a list of strings
                raise ScraperException from TypeError
        else:
            raise ScraperException from TypeError
        return result

    def find_all(self, xpath: str, document: html.HtmlElement = None) -> typing.List[html.HtmlElement]:
        """Execute an XPath expression that returns one or more HtmlElements and validate the result's type.

        Args:
            xpath: The XPath expression to execute
            document: The document to execute the expression on
        Returns:
            A list of all matching elements
        Raises:
            ScraperException: When the result is not a list of HtmlElements
        """
        result = self.select(xpath, document)
        if not isinstance(result, list):
            raise ScraperException('Result of "{}" is not a list of HtmlElements'.format(xpath)) from TypeError
        return result

    def navigate(self, xpaths: typing.List[str], url: str) -> typing.Iterable[typing.Tuple[str, html.HtmlElement]]:
        """Navigate through multiple pages.

        Note that when a given XPath expression returns multiple elements / strings, this method
        will only consider the first element of that list.

        Args:
            xpaths: List of XPath expressions pointing to links or link-containing elements
            url: The URL to start the navigation at
        Yields:
            A touple of the currently visited url and document
        Returns:
            A tuple of the final url and document
        Raises:
            ValueError: When either xpaths or url were not provided
            ScraperError: When an XPath expression did not select a link or
                link-containing element
        """
        if not xpaths:
            raise ValueError('No XPath(s) for selection provided')
        if not url:
            raise ValueError('No URL provided to start navigation at')
        document = self.fetch(url)
        link = None  # type: str
        for xpath in xpaths:
            selection = self.select(xpath, document)
            if isinstance(selection, str):
                # Selection is string (most likely an URL)
                link = selection
            elif isinstance(selection, html.HtmlElement):
                # Selection is an HTML element that SHOULD contain a href attribute
                try:
                    link = selection.get('href')
                except KeyError as err:
                    raise ScraperException from err
            elif isinstance(selection, list):
                # Selection is a list of something
                if not len(selection):
                    raise NoSuchElementException(xpath)
                elem = selection[0]
                if isinstance(elem, str):
                    link = elem
                elif isinstance(elem, html.HtmlElement):
                    try:
                        link = elem.get('href')
                    except KeyError as err:
                        raise ScraperException from err
                else:
                    # Every other type cannot be used for navigation
                    raise ScraperException('Cannot perform navigation with result of type {} from XPath "{}"'
                                           .format(type(selection), xpath))
            else:
                # Every other type cannot be used for navigation
                raise ScraperException('Cannot perform navigation with result of type {} from XPath "{}"'
                                       .format(type(selection), xpath))
            document = self.fetch(link)
            yield link, document
        return link, document

    @property
    def status(self) -> typing.Optional[float]:
        return self._current_status

    @property
    def location(self) -> typing.Optional[str]:
        return self._current_location

    @property
    def document(self) -> typing.Optional[html.HtmlElement]:
        return self._current_document

    @property
    def cookies(self) -> requests.cookies.RequestsCookieJar:
        return self.session.cookies

    @cookies.deleter
    def cookies(self) -> ():
        self.session.cookies.clear()

    def __repr__(self) -> str:
        return '<{}(location={}, status={})>'.format(self.__class__, self.location, self.status)
