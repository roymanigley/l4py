import abc
import inspect
import logging
import logging.config
import platform

from l4py import utils
from l4py.formatters import TextFormatter, JsonFormatter


def _get_caller_info():
    frame = inspect.currentframe().f_back.f_back
    module_name = frame.f_globals.get('__name__', '<unknown>')
    class_name = None
    if 'self' in frame.f_locals:
        class_name = type(frame.f_locals['self']).__name__
    return module_name, class_name


def get_logger(logger_name: str = None) -> logging.Logger:
    if logger_name is None:
        module_name, class_name = _get_caller_info()
        logger_name = '.'.join([s for s in [module_name, class_name] if s is not None])
    return logging.getLogger(logger_name)


class AbstractLoggingBuilder:
    _text_formatter: type[logging.Formatter] = TextFormatter
    _json_formatter: type[logging.Formatter] = JsonFormatter

    _loggers: dict[str, int] = {}
    _root_level: int = None

    _filters: dict[str, type[logging.Filter]] = {}
    _console_enabled: bool = True
    _console_format: str = None
    _console_formatter: type[logging.Formatter] = _text_formatter

    _file_enabled: bool = True
    _file: str = f'{utils.get_app_name()}-{platform.uname().node}.log'
    _file_max_size: int = 10 * 1024 * 1024  # 10 MB (default)
    _file_max_count: int = 5  # Default 5 backup files
    _file_format: str = None
    _file_formatter: type[logging.Formatter] = _json_formatter

    def console_json(self, value: bool) -> 'AbstractLoggingBuilder':
        self._console_formatter = JsonFormatter if value else TextFormatter
        return self

    def file(self, file_name: str) -> 'AbstractLoggingBuilder':
        self._file = file_name
        return self

    def file_json(self, value: bool) -> 'AbstractLoggingBuilder':
        self._file_formatter = JsonFormatter if value else TextFormatter
        return self

    def file_max_size_mb(self, size_in_mb: int) -> 'AbstractLoggingBuilder':
        self._file_max_size = size_in_mb * 1024 * 1024
        return self

    def file_max_count(self, count: int) -> 'AbstractLoggingBuilder':
        self._file_max_count = count
        return self

    def console_enabled(self, enabled: bool) -> 'AbstractLoggingBuilder':
        self._console_enabled = enabled
        return self

    def file_enabled(self, enabled: bool) -> 'AbstractLoggingBuilder':
        self._file_enabled = enabled
        return self

    def console_formatter(self, formatter: type[logging.Formatter]) -> 'AbstractLoggingBuilder':
        self._console_formatter = formatter
        return self

    def console_format(self, format: str) -> 'AbstractLoggingBuilder':
        self._console_format = format
        return self

    def file_formatter(self, formatter: type[logging.Formatter]) -> 'AbstractLoggingBuilder':
        self._file_formatter = formatter
        return self

    def file_format(self, format: str) -> 'AbstractLoggingBuilder':
        self._file_format = format
        return self

    def add_filter(self, name: str, filter: type[logging.Filter]) -> 'AbstractLoggingBuilder':
        self._filters[name] = {'()', filter}
        return self

    def add_logger(self, name: str, log_level: int) -> 'AbstractLoggingBuilder':
        self._loggers[name] = log_level
        return self

    def add_root_logger(self, log_level: int) -> 'AbstractLoggingBuilder':
        self._root_level = log_level
        return self

    @abc.abstractmethod
    def build_config(self) -> dict:
        pass

    def init(self) -> None:
        config_dict = self.build_config()
        logging.config.dictConfig(config_dict)

    def build_default_config(self) -> dict:

        handlers_names = []
        formatters = {}
        handlers = {}

        if self._console_enabled:
            if self._console_format:
                formatters['console'] = {
                    'format': self._console_format,
                }
            else:
                formatters['console'] = {
                    '()': f'{self._console_formatter.__module__}.{self._console_formatter.__name__}',
                }
            handlers_names.append('console')
            handlers['console'] = {
                'class': 'logging.StreamHandler',
                'formatter': 'console',
                'filters': self._filters.keys()
            }

        if self._file_enabled:
            if self._console_format:
                formatters['file'] = {
                    'format': self._file_format,
                }
            else:
                formatters['file'] = {
                    '()': f'{self._file_formatter.__module__}.{self._file_formatter.__name__}',
                }
            handlers_names.append('file')
            handlers['file'] = {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': self._file,
                'maxBytes': self._file_max_size,
                'backupCount': self._file_max_count,
                'formatter': 'file',
                'filters': self._filters.keys()
            }

        config_dict = {
            'version': 1,
            'disable_existing_loggers': False,
            'filters': self._filters,
            'handlers': handlers,
            'root': {
                'level': self._root_level if self._root_level else utils.get_log_level_root_from_env(),
                "handlers": handlers_names,
                "filters": self._filters.keys(),
                'propagate': True,
            },
            'loggers': {
            },
            'formatters': formatters
        }

        for name, level in self._loggers.items():
            config_dict['loggers'][name] = {
                'handlers': handlers_names,
                'level': level,
                'propagate': True,
            }

        for logger_level_dict in utils.get_log_levels_env():
            config_dict['loggers'][logger_level_dict['logger']] = {
                'handlers': handlers_names,
                'level': logger_level_dict['level'],
                'propagate': True,
            }

        return config_dict


class LogConfigBuilder(AbstractLoggingBuilder):

    def build_config(self) -> dict:
        config_dict = self.build_default_config()
        return config_dict


class LogConfigBuilderDjango(AbstractLoggingBuilder):
    _django_log_level = utils.get_log_level_root_from_env()
    _show_sql = False

    def django_log_level(self, log_level: int) -> 'LogConfigBuilderDjango':
        self._django_log_level = log_level
        return self

    def show_sql(self, show_sql: bool) -> 'LogConfigBuilderDjango':
        self._show_sql = show_sql
        return self

    def build_config(self) -> dict:
        config_dict = self.build_default_config()

        handlers_names = []

        if self._console_enabled:
            handlers_names.append('console')

        if self._file_enabled:
            handlers_names.append('file')

        config_dict['loggers']['django'] = {
            'handlers': config_dict['root']['handlers'],
            'level': self._django_log_level,
            'propagate': False,
        }

        if self.show_sql:
            config_dict['loggers']['django.db.backends'] = {
                'handlers': config_dict['root']['handlers'],
                'level': 'DEBUG',
                'propagate': False,
            }

        return config_dict
