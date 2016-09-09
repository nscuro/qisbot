import typing
import requests
from lxml import html
from lxml.etree import ParserError
from lxml.etree import XPathEvalError


def fetch_source(url: str, session: requests.Session = None) -> str:
    """Fetch the source of a page from the given URL.

    Args:
        url: URL to fetch the page source from
        session: Session to use for the request
    Returns:
        The fetched source
    Raises:
        ValueError: When no URL was given
        requests.RequestException: When the server responded with HTTP 4xx or 5xx
    """
    if not url:
        raise ValueError('Target URL must not be blank')
    response = session.get(url) if session else requests.get(url)
    response.raise_for_status()
    return response.text


def select_all(source: str, xpath: str) -> typing.List[html.HtmlElement]:
    """Select all elements matching a given xpath expression.

    Args:
        source: HTML source to perform selection on
        xpath: XPath expression
    Returns:
        List of matching elements
    Raises:
        ValueError: When source contains malformed URL or xpath is not a valid expression
    """
    try:
        parsed_source = html.fromstring(source)
    except ParserError as perr:
        raise ValueError('Source contains malformed HTML') from perr
    else:
        try:
            selected_elements = parsed_source.xpath(xpath)
        except XPathEvalError as xperr:
            raise ValueError('{} is not a valid XPath expression'.format(xpath)) from xperr
        else:
            return selected_elements


def select(source: str, xpath: str) -> typing.Optional[html.HtmlElement]:
    """Select the first element matching a given xpath expression.

    Args:
        source: HTML source to perform selection on
        xpath: XPath expression
    Returns:
        A matching element or None
    Raises:
        ValueError: When source contains malformed URL or xpath is not a valid expression
    """
    selected_elements = select_all(source, xpath)
    return selected_elements[0] if selected_elements else None
