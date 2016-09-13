import typing

import requests
from lxml import html
from lxml.etree import ParserError
from lxml.etree import XPathEvalError


class ScraperError(IOError):
    """Raised when a scraper function encounters an internal error."""
    pass


class ElementNotFoundError(LookupError):
    """Raised when a requested html element was not found."""
    pass


class FetchedPage(object):
    """Container class that encapsulates basic web page properties."""

    def __init__(self, source: str, url: str = None):
        """
        Args:
            source: HTML source of the fetched page
            url: The URL of the given page
        Raises:
            ScraperError: When parsing the given source failed
        """
        try:
            self.document = html.document_fromstring(source)  # type: html.HtmlElement
        except ParserError as perr:
            raise ScraperError('Page source contains malformed HTML') from perr
        self.url = url
        if self.url:
            self.document.make_links_absolute(self.url, resolve_base_href=True)

    def __repr__(self):
        return '<{}>'.format(self.__class__)


def fetch_source(url: str, session: requests.Session = None) -> FetchedPage:
    """Fetch the source of a page from the given URL.

    Args:
        url: URL to fetch the page source from
        session: Session to use for the request
    Returns:
        A FetchedPage instance containing source and URL of the page fetched
    Raises:
        ValueError: When no URL was provided
        requests.RequestException: When the server responded with HTTP 4xx or 5xx
    """
    if not url:
        raise ValueError('Target URL must not be blank')
    response = session.get(url) if session else requests.get(url)
    response.raise_for_status()
    return FetchedPage(response.text, url)


def select_all(page: FetchedPage, xpath: str) -> typing.List[html.HtmlElement]:
    """Select all elements matching a given xpath expression.

    Args:
        page: Fetched page to perform the selection on
        xpath: XPath expression
    Returns:
        List of matching elements
    Raises:
        ScraperError: When source contains malformed URL or xpath is not a valid expression
    """
    if not page or page.document is None:
        raise ValueError('No fetched page provided')
    try:
        selected_elements = page.document.xpath(xpath)
    except XPathEvalError as xperr:
        raise ScraperError('{} is not a valid XPath expression'.format(xpath)) from xperr
    else:
        return selected_elements


def select(page: FetchedPage, xpath: str) -> typing.Optional[html.HtmlElement]:
    """Select the first element matching a given xpath expression.

    Args:
        page: Fetched page to perform the selection on
        xpath: XPath expression
    Returns:
        A matching element or None
    Raises:
        ScraperError: When source contains malformed URL or xpath is not a valid expression
    """
    selected_elements = select_all(page, xpath)
    return selected_elements[0] if selected_elements else None


def navigate(launch_url: str, xpaths: typing.List[str], session: requests.Session = None) -> FetchedPage:
    """Navigate through multiple pages.

    Args:
        launch_url: Starting URL of the navigation
        xpaths: List of xpaths pointing to the given links (use /@href)
        session: The session to use
    Returns:
        A FetchedPage instance of the final destination
    Raises:
        ElementNotFoundError: When a links could not be found
        ScraperError: When an invalid or no URL was selected using XPath
    """
    fetched_page = fetch_source(launch_url, session=session)
    for xpath in xpaths:
        link = select(fetched_page, xpath)
        if link is None:
            raise ElementNotFoundError('Navigation failed in step #{}: Unable to locate link at "{}"'
                                       .format(xpaths.index(xpath), xpath))
        try:
            fetched_page = fetch_source(str(link), session=session)
        except requests.exceptions.MissingSchema as err:
            raise ScraperError('XPath "{}" did not explicitly select an (absolute) URL'.format(xpath)) from err
    return fetched_page
