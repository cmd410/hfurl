__version__ = '0.2.0'

from collections import namedtuple
from typing import NamedTuple, Optional
from functools import cache


class InvalidURL(Exception):
    """Raised when a URL has an invalid form.
    """
    pass


class NoHost(InvalidURL): pass
class CredentialsError(InvalidURL): pass
class UnknownScheme(InvalidURL): pass


_DEFAULT_PORTS = {
    'http': 80,
    'https': 443,
    'ftp': 21,
    'sftp': 22,
    'gemini': 1965,
    'gopher': 70
}


url_parse_result = namedtuple(
    'URLParseResult',
    ['scheme', 'host', 'path', 'port',
     'username', 'password', 'query', 'fragment'])


class URLParseResult(NamedTuple):
    scheme: str
    host: str
    path: str
    port: int
    username: str
    password: str
    query: str
    fragment: str

    @cache
    def __str__(self) -> str:
        url = f'{self.scheme}://'
        if self.username:
            url += self.username
            if self.password:
                url += f':{self.password}'
            url += '@'
        url += self.host

        if self.port != -1 and self.port != _DEFAULT_PORTS.get(self.scheme):
            url += f':{self.port}'

        url += self.path
        if self.query: url += f'?{self.query}'
        if self.fragment: url += f'#{self.fragment}'
        return url


def parse_url(url: str,
              default_scheme: str = 'https',
              schemes: Optional[dict] = None,
              validate_scheme: bool = True
              ) -> url_parse_result:
    """Parses given url, returns namedtuple of
    (scheme, host, path, port, username, password)

    Whenever possible it will try to deduce port from
    given schema, if no port explicitly specified.
    
    Params:
    url - url to parse
    default_scheme - scheme to fallback to if none in url
    schemes - a mapping of scheme: default_port
    validate_scheme - if True, checks scheme against given schemes or predefined protocols in the module 

    Raises one of
        - InvalidURL - generic url format error(base class for others)
        - NoHost - no host provided
        - CredentialsError - Invalid credentials in url
    """
    url = str(url).strip()

    # Parse scheme
    scheme = default_scheme
    if '://' in url:
        scheme, host = url.split('://', maxsplit=1)
    else:
        host = url

    # Assume port based on scheme
    scheme_set = schemes or _DEFAULT_PORTS
    port = scheme_set.get(scheme, -1)
    if validate_scheme and port == -1:
        raise UnknownScheme(f"unknown scheme: {scheme!r}, expected one of {scheme_set}")

    if not host:
        raise NoHost(url)

    # Parse username and password
    username, password = '', ''
    if '@' in host:
        at_pos = host.find('@')
        user_info = host[:at_pos]
        host = host[at_pos + 1:]
        if ':' not in user_info:
            username = user_info
            password = ''
        else:
            username, password = user_info.split(':')
        if not username:
            raise CredentialsError(url)

    if password and not username:
        raise CredentialsError(url)

    # Parse path
    if '/' not in host:
        path = '/'
    else:
        host, path = host.split('/', maxsplit=1)
        path = '/' + path

    query = ''
    if '?' in path:
        path, query = path.split('?', maxsplit=1)

    if not host:
        raise NoHost(url)

    # Parse port
    if '[' in host and (closing := host.find(']')) != -1:
        if closing != len(host) - 1:
            if host[closing + 1] == ':':
                port = int(host[closing + 2:])
                host = host[:closing + 1]
    elif ':' in host:
        host, port_str = host.split(':', maxsplit=1)
        if not all([host, port_str]):
            raise InvalidURL(url)
        port = int(port_str)

    fragment = ''
    if query:
        if (fragment_idx := query.find('#')) != -1:
            fragment = query[fragment_idx + 1:]
            query = query[:fragment_idx]
    else:
        if (fragment_idx := path.find('#')) != -1:
            fragment = path[fragment_idx + 1:]
            path = path[:fragment_idx]

    return URLParseResult(
        scheme,
        host,
        path,
        port,
        username,
        password,
        query,
        fragment
    )
