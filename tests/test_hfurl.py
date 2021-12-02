from itertools import product

import pytest

from hfurl import __version__, URLParseResult, parse_url, _DEFAULT_PORTS


def test_version():
    assert __version__ == '0.1.0'


def generate_url():
    protos = ('http', 'https', 'ftp', 'sftp', 'gemini', 'gopher', 'scheme', '')
    domains = (
        'example.com', '[2001:db8::]', '127.0.0.1'
    )
    ports = (8080, 6204, '')
    usernames = ('username', '')
    passwords = ('password', '')
    paths = (
        '/',
        '/some/path'
    )
    queries = ('', '?param=value')
    fragments = ('', 'fragment')

    for proto, user, password, host, port, path, query, fragment in \
            product(protos, usernames, passwords,
                    domains, ports, paths, queries, fragments):
        url = ''
        if proto:
            url = f'{proto}://'
            if not port:
                port = 443 if proto == 'https' else 80
        else:
            proto = 'https'
        if user:
            url += f'{user}'
            if password:
                url += f':{password}'
            url += '@'
        url += f'{host}'
        if port:
            url += f':{port}'
        url += f'{path}{query}'
        if fragment:
            url += f'#{fragment}'
        if not port:
            port = _DEFAULT_PORTS.get(proto, -1)

        yield url, URLParseResult(
            proto or 'https',
            host,
            path,
            port,
            user,
            password if user else '',
            query[1:],
            fragment)


@pytest.mark.parametrize("url,expected", generate_url())
def test_url(url, expected):
    assert parse_url(url, 'https') == expected
