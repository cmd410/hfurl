<h1>HFURL - Human-friendly URL</h1>

This is a tiny python library taht provides parsing for human-firendly.
Completely disregarding RFC it correctly parses url with no schema
(eg. `example.com` is equivalent to `https://example.com/`).

Useful when reading input URL from user, who as we al know, often omit schema.

## Usage

```python
from hfurl import parse_url

url = parse_url("example.com:443/about")
assert url.host == "example.com"
```
