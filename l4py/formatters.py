import json
import logging
from datetime import datetime

from l4py import utils


class FormatTimeMixin():
    def formatTime(self, record, datefmt=None):
        ct = datetime.fromtimestamp(record.created)
        if datefmt:
            return ct.strftime(datefmt)
        else:
            return ct.strftime("%Y-%m-%dT%H:%M:%S.") + f"{int(record.msecs):03d}"


class JsonFormatter(FormatTimeMixin, logging.Formatter):

    def __init__(self, app_name=utils.get_app_name()):
        super().__init__()
        self.app_name = app_name

    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "app_name": self.app_name,
            "logger_name": record.name,
            "level": record.levelname,
            "file_name": record.filename,
            "line_number": record.lineno,
            "function_name": record.funcName,
            "message": record.msg,
        }
        return json.dumps(log_record)


class TextFormatter(FormatTimeMixin, logging.Formatter):

    def __init__(self, app_name=utils.get_app_name()):
        super().__init__()
        self.app_name = app_name

    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "app_name": self.app_name,
            "logger_name": record.name,
            "level": record.levelname,
            "file_name": record.filename,
            "line_number": record.lineno,
            "function_name": record.funcName,
            "message": record.msg,
        }
        return '{timestamp} [{level:<8}] {app_name} {file_name}:{line_number} {function_name}: {message}'.format(
            **log_record)
