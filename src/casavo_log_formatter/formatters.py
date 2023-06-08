import importlib
import importlib.util
import logging.config
import typing
from datetime import datetime, timezone


class CasavoJsonFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._datetime_from_timestamp_fn = datetime.fromtimestamp
        self._dumps = self._select_serializer()

    def format(self, record: logging.LogRecord) -> str:
        try:
            msg = record.getMessage()
        except TypeError:
            msg = record.msg

        extra = {
            "type": "log",
        }

        exc = ""
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
            extra["class"] = str(record.exc_info[0])
        if record.exc_text:
            exc += record.exc_text
        if record.stack_info:
            if exc:
                exc += "\n"
            exc += self.formatStack(record.stack_info)

        if len(exc) > 0:
            extra["traceback"] = exc
            extra["type"] = "exception"

        if type(msg) not in {dict, list, str, int, float, bool, None}:
            msg = str(msg)

        message = {
            "datetime": self._datetime_from_timestamp_fn(record.created, timezone.utc),
            "level": record.levelname,
            "message": msg,
            "channel": record.name,
            "pid": record.process,
            "context": {
                "processname": record.processName,
                "pathname": record.pathname,
                "module": record.module,
                "function": record.funcName,
                "lineno": record.lineno,
            },
            "extra": extra,
        }

        return self._dumps(message)

    def _select_serializer(self) -> typing.Callable[[typing.Any], str]:
        return _orjson_serializer if importlib.util.find_spec("orjson") else _stdlib_serializer


def _orjson_serializer(obj):
    import orjson

    return orjson.dumps(obj, option=orjson.OPT_UTC_Z).decode()


def _stdlib_serializer(obj):
    import json

    def default_serializer(value):
        if not isinstance(value, datetime):
            str(value)
        value: datetime
        if value.tzinfo:
            return f"{value.utcfromtimestamp(value.timestamp()).isoformat()}Z"
        return f"{value.isoformat()}Z"

    return json.dumps(
        obj,
        default=default_serializer,
        ensure_ascii=False,
    )
