import datetime
import json
import logging
import sys
from logging import LogRecord
from typing import Any, Callable
from unittest import TestCase, mock

from casavo_log_formatter import formatters
from casavo_log_formatter.formatters import _orjson_serializer, _stdlib_serializer


class JsonFormatterTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.maxDiff = None

    def test_formats_correctly(self):
        stdlib_json_formatter, orjson_json_formatter = self._default_formatters()

        expected_result = {
            "datetime": "2021-08-25T08:30:00.123456Z",
            "level": "INFO",
            "message": "The error message value",
            "channel": "library.module",
            "pid": 4321,
            "context": {
                "processname": "MainProcess",
                "pathname": "library/module.py",
                "module": "module",
                "function": None,
                "lineno": 1234,
            },
            "extra": {"type": "log"},
        }

        log_record = self._log_record_builder()
        stdlib_result, orjson_result = (
            json.loads(f.format(log_record)) for f in (stdlib_json_formatter, orjson_json_formatter)
        )

        self.assertEqual(expected_result, stdlib_result)
        self.assertEqual(expected_result, orjson_result)
        self.assertEqual(stdlib_result, orjson_result)

    def test_takes_the_logrecord_message_field_if_it_cant_invoke_getMessage_to_format_msg_with_args(
        self,
    ):
        stdlib_json_formatter, orjson_json_formatter = self._default_formatters()

        expected_result = {
            "datetime": "2021-08-25T08:30:00.123456Z",
            "level": "INFO",
            "message": "This will trigger a TypeError since the LogRecord has an args param set",
            "channel": "library.module",
            "pid": 4321,
            "context": {
                "processname": "MainProcess",
                "pathname": "library/module.py",
                "module": "module",
                "function": None,
                "lineno": 1234,
            },
            "extra": {"type": "log"},
        }

        log_record = self._log_record_builder(
            msg="This will trigger a TypeError since the LogRecord has an args param set"
        )
        stdlib_result, orjson_result = (
            json.loads(f.format(log_record)) for f in (stdlib_json_formatter, orjson_json_formatter)
        )

        self.assertEqual(expected_result, stdlib_result)
        self.assertEqual(expected_result, orjson_result)
        self.assertEqual(stdlib_result, orjson_result)

    @mock.patch(
        "casavo_log_formatter.formatters.CasavoJsonFormatter.formatException", lambda *_: "Traceback"
    )
    def test_formats_exception_info_into_extra_field(self):
        stdlib_json_formatter, orjson_json_formatter = self._default_formatters()

        exc_info = self._exception_builder(TypeError)
        expected_result = {
            "datetime": "2021-08-25T08:30:00.123456Z",
            "level": "INFO",
            "message": "The error message value",
            "channel": "library.module",
            "pid": 4321,
            "context": {
                "processname": "MainProcess",
                "pathname": "library/module.py",
                "module": "module",
                "function": None,
                "lineno": 1234,
            },
            "extra": {"type": "exception", "class": "<class 'TypeError'>", "traceback": "Traceback"},
        }

        log_record = self._log_record_builder(exc_info=exc_info)
        stdlib_result, orjson_result = (
            json.loads(f.format(log_record)) for f in (stdlib_json_formatter, orjson_json_formatter)
        )

        self.assertEqual(expected_result, stdlib_result)
        self.assertEqual(expected_result, orjson_result)
        self.assertEqual(stdlib_result, orjson_result)

    def test_formats_exception_info_with_exc_text_data_into_extra_field(self):
        stdlib_json_formatter, orjson_json_formatter = self._default_formatters()

        exc_info = self._exception_builder(TypeError)
        expected_result = {
            "datetime": "2021-08-25T08:30:00.123456Z",
            "level": "INFO",
            "message": "The error message value",
            "channel": "library.module",
            "pid": 4321,
            "context": {
                "processname": "MainProcess",
                "pathname": "library/module.py",
                "module": "module",
                "function": None,
                "lineno": 1234,
            },
            "extra": {
                "type": "exception",
                "class": "<class 'TypeError'>",
                "traceback": "Supplemental text",
            },
        }

        log_record = self._log_record_builder(exc_info=exc_info, exc_text="Supplemental text")
        stdlib_result, orjson_result = (
            json.loads(f.format(log_record)) for f in (stdlib_json_formatter, orjson_json_formatter)
        )

        self.assertEqual(expected_result, stdlib_result)
        self.assertEqual(expected_result, orjson_result)
        self.assertEqual(stdlib_result, orjson_result)

    def test_formats_exception_info_with_stack_info(self):
        stdlib_json_formatter, orjson_json_formatter = self._default_formatters()

        expected_result = {
            "datetime": "2021-08-25T08:30:00.123456Z",
            "level": "INFO",
            "message": "The error message value",
            "channel": "library.module",
            "pid": 4321,
            "context": {
                "processname": "MainProcess",
                "pathname": "library/module.py",
                "module": "module",
                "function": None,
                "lineno": 1234,
            },
            "extra": {
                "type": "exception",
                "traceback": "Supplemental text\nStack info",
            },
        }

        log_record = self._log_record_builder(exc_text="Supplemental text", sinfo="Stack info")
        stdlib_result, orjson_result = (
            json.loads(f.format(log_record)) for f in (stdlib_json_formatter, orjson_json_formatter)
        )

        self.assertEqual(expected_result, stdlib_result)
        self.assertEqual(expected_result, orjson_result)
        self.assertEqual(stdlib_result, orjson_result)

        # with no exc_text, does not concatenate with stackinfo
        log_record = self._log_record_builder(sinfo="Stack info")
        stdlib_result, orjson_result = (
            json.loads(f.format(log_record)) for f in (stdlib_json_formatter, orjson_json_formatter)
        )

        expected_result["extra"]["traceback"] = "Stack info"

        self.assertEqual(expected_result, stdlib_result)
        self.assertEqual(expected_result, orjson_result)
        self.assertEqual(stdlib_result, orjson_result)

    def test_casts_to_string_msg_if_its_not_a_json_serializable_primitive(self):
        stdlib_json_formatter, orjson_json_formatter = self._default_formatters()

        expected_result = {
            "datetime": "2021-08-25T08:30:00.123456Z",
            "level": "INFO",
            "message": "<class 'TypeError'>",
            "channel": "library.module",
            "pid": 4321,
            "context": {
                "processname": "MainProcess",
                "pathname": "library/module.py",
                "module": "module",
                "function": None,
                "lineno": 1234,
            },
            "extra": {
                "type": "log",
            },
        }

        log_record = self._log_record_builder(msg=TypeError)
        stdlib_result, orjson_result = (
            json.loads(f.format(log_record)) for f in (stdlib_json_formatter, orjson_json_formatter)
        )

        self.assertEqual(expected_result, stdlib_result)
        self.assertEqual(expected_result, orjson_result)
        self.assertEqual(stdlib_result, orjson_result)

    def _json_formatter_builder(
        self, *, with_date: datetime, with_serializer: Callable[[Any], str] = None
    ):
        json_formatter = formatters.CasavoJsonFormatter()
        json_formatter._datetime_from_timestamp_fn = lambda *_: with_date
        if not with_serializer:
            return json_formatter
        json_formatter._dumps = with_serializer
        return json_formatter

    def _log_record_builder(
        self,
        *,
        lineno: int = 1234,
        pid: int = 4321,
        msg: str = "The error message %s",
        exc_info=None,
        exc_text=None,
        sinfo=None,
    ):
        log_record = LogRecord(
            name="library.module",
            level=logging.INFO,
            pathname="library/module.py",
            lineno=lineno,
            msg=msg,
            args=("value",),
            exc_info=exc_info,
            func=None,
            sinfo=sinfo,
        )
        log_record.process = pid
        log_record.exc_text = exc_text
        return log_record

    def _exception_builder(self, exception):
        try:
            raise exception
        except:  # noqa
            return sys.exc_info()

    def _default_formatters(self):
        return (
            self._json_formatter_builder(
                with_date=datetime.datetime(2021, 8, 25, 8, 30, 0, 123456, datetime.timezone.utc),
                with_serializer=_stdlib_serializer,
            ),
            self._json_formatter_builder(
                with_date=datetime.datetime(2021, 8, 25, 8, 30, 0, 123456, datetime.timezone.utc),
                with_serializer=_orjson_serializer,
            ),
        )


class SerializersTest(TestCase):
    def test_serialize_accented_letters_the_same(self):
        test_data = "àèìòù"
        expected_result = '"àèìòù"'

        stdlib = _stdlib_serializer(test_data)
        orjson = _orjson_serializer(test_data)

        self.assertEqual(stdlib, expected_result)
        self.assertEqual(orjson, expected_result)
        self.assertEqual(stdlib, orjson)

    def test_serialize_datetimes_the_same_in_isoformat_with_z(self):
        test_data = datetime.datetime(2021, 8, 25, 8, 30, 0, 123456, datetime.timezone.utc)
        expected_result = '"2021-08-25T08:30:00.123456Z"'

        stdlib = _stdlib_serializer(test_data)
        orjson = _orjson_serializer(test_data)

        self.assertEqual(stdlib, expected_result)
        self.assertEqual(orjson, expected_result)
        self.assertEqual(stdlib, orjson)
