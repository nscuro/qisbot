import typing

import requests
from lxml import html
from lxml.etree import ParseError
from lxml.etree import XPathEvalError, XPathSyntaxError

from qisbot.exceptions import ScraperException


class Scraper(object):
    def __init__(self, session: requests.Session = None):
        self.session = session or requests.Session()
        self._current_document = None  # type: html.HtmlElement
        self._current_location = None  # type: str
        self._current_status = None  # type: int
        self.allow_redirects = True

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
            raise ScraperException from err
        return result

    def check(self, xpath: str, document: html.HtmlElement = None) -> bool:
        """Execute a boolean XPath expression.

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

    def navigate(self, xpaths: typing.List[str], url: str) -> typing.Generator[
                 typing.Tuple[str, html.HtmlElement], None, typing.Tuple[str, html.HtmlElement]]:
        """Navigate through multiple pages.

        Args:
            xpaths: List of XPath expressions pointing to links or link-containing elements
            url: The URL to start the navigation at
        Yields:
            A touple of the currently visited url and document
        Returns:
            A touple of the final url and document
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
                link = selection
            elif isinstance(selection, html.HtmlElement):
                try:
                    link = selection.get('href')
                except KeyError as err:
                    raise ScraperException from err
            else:
                raise ScraperException('Cannot perform navigation with result of type {} from XPath "{}"'
                                       .format(type(selection), xpath))
            document = self.fetch(link)
            yield link, document
        return link, document

    @property
    def status(self):
        return self._current_status

    @property
    def location(self):
        return self._current_location

    @property
    def document(self):
        return self._current_document

    @property
    def cookies(self):
        return self.session.cookies

    @cookies.deleter
    def cookies(self):
        self.session.cookies.clear()

    def __repr__(self):
        return '<{}(location={})>'.format(self.__class__, self._current_location)
