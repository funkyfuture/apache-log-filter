apache-log-filter
=================

A Python 3 library to retrieve Apache web server accesses filtered by sets of filters. You can use white-/blacklisting filters with regular expressions on a raw line or more sophisticated on certain log fields, including comparison on numerical and date fields. There's also a generic filter to ignore bots.

Be aware that the library isn't very mature yet. I needed it and found nothing comparable. You're invited to contribute.

If you are looking for a CLI-usable toolkit, you may be interested in ```logtools``` ([GitHub](https://github.com/adamhadani/logtools) / [PyPI](https://pypi.python.org/pypi/logtools)).

## Example

TODO

## Dependencies

- apache-log-parser => 1.4.0 ([GitHub](https://github.com/rory/apache-log-parser) / [PyPI](https://pypi.python.org/pypi/apache-log-parser))
  - user-agents ([GitHub](https://github.com/selwin/python-user-agents) / [PyPI](https://pypi.python.org/pypi/user-agents))
    - ua-parser ([GitHub](https://github.com/tobie/ua-parser) / [PyPI](https://pypi.python.org/pypi/ua-parser))

## Installation

```
python3 setup.py install
```

or if you want to hack it:

```
python3 setup.py develop
```

## Roadmap

- Inline documentation
- Testing, srsly
- Caching
- Filter bots also by IP
- Fork something that filters generic log formats
