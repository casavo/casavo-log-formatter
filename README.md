# casavo-logger

An utility library that exposes a pre-configured log formatter for the Casavo JSON logging format.

## Usage

Referring to https://docs.python.org/3/library/logging.config.html#logging-config-dictschema,
we suggest to configure your logging `dictConfig` by adding those 2 keys:

```python
formatters = {
    "simple": {
        "format": "%(levelname)s %(message)s",
        "datefmt": "%H:%M:%S",
    },
    "standard": {
        "class": "casavo_log_formatter.formatters.CasavoJsonFormatter"
    },
}
```

```python
handlers = {
    "stdout": {
        "level": "DEBUG",
        "class": "logging.StreamHandler",
        "formatter": "standard"
        if settings.ENVIRONMENT in ["staging", "production"]  # or whatever you use to specify the env
        else "simple",
    },
}
```

This will configure a simple log format for dev and the fully featured formatter for staging + dev.

## Development

* Have a local python >=3.9
* `python -m venv .venv`
* `pip install -r requirements.txt`
* `pre-commit install`
* `pip install -e .`

### Test

`make test` or `nox` to launch the test matrix against Python 3.9, 3.10, 3.11

### Uploading on PyPI

* `make upload`
