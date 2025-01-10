import inspect
import logging
import logging.config
import platform

from l4py import utils
from l4py.formatters import TextFormatter, JsonFormatter


def __get_caller_info():
    frame = inspect.currentframe().f_back.f_back
    module_name = frame.f_globals.get('__name__', '<unknown>')
    class_name = None
    if 'self' in frame.f_locals:
        class_name = type(frame.f_locals['self']).__name__
    return module_name, class_name


def get_logger(logger_name: str = None) -> logging.Logger:
    if logger_name is None:
        module_name, class_name = __get_caller_info()
        logger_name = ''.join([s for s in [module_name, class_name] if s is not None])
    return logging.getLogger(logger_name)


class LogConfigBuilder:
    __text_formatter = TextFormatter()
    __json_formatter = JsonFormatter()

    __console_json = False

    __file = f'{utils.get_app_name()}-{platform.uname().node}.log'
    __file_json = True
    __file_max_size = 10 * 1024 * 1024  # 10 MB (default)
    __file_max_count = 5  # Default 5 backup files

    def console_json(self, value: bool) -> 'LogConfigBuilder':
        self.__console_json = value
        return self

    def file(self, file_name: str) -> 'LogConfigBuilder':
        self.__file = file_name
        return self

    def file_json(self, value: bool) -> 'LogConfigBuilder':
        self.__file_json = value
        return self

    def file_max_size_mb(self, size_in_mb: int) -> 'LogConfigBuilder':
        self.__file_max_size = size_in_mb * 1024 * 1024
        return self

    def file_max_count(self, count: int) -> 'LogConfigBuilder':
        self.__file_max_count = count
        return self

    def build_config_dict(self) -> dict:
        config_dict = {
            'version': 1,
            'disable_existing_loggers': False,
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'console',
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': self.__file,
                    'maxBytes': self.__file_max_size,
                    'backupCount': self.__file_max_count,
                    'formatter': 'file',
                },
            },
            'root': {
                'level': utils.get_log_level_root(),
                "handlers": [
                    "console",
                    "file"
                ]
            },
            'loggers': {
            },
            'formatters': {
                'file': {
                    '()': f'{JsonFormatter.__module__}.{JsonFormatter.__name__}' if self.__file_json else f'{TextFormatter.__module__}.{TextFormatter.__name__}',
                },
                'console': {
                    '()': f'{JsonFormatter.__module__}.{JsonFormatter.__name__}' if self.__console_json else f'{TextFormatter.__module__}.{TextFormatter.__name__}',
                },
            },
        }

        for logger_level_dict in utils.get_log_levels_env():
            config_dict['loggers'][logger_level_dict['logger']] = {
                'handlers': ['console', 'file'],
                'level': logger_level_dict['level'],
                'propagate': True,
            }

        return config_dict

    def init(self) -> None:
        config_dict = self.build_config_dict()
        logging.config.dictConfig(config_dict)

    def build_config_dict_for_django(self, django_log_level=logging.INFO, show_sql=False) -> dict:
        config_dict = self.build_config_dict()

        config_dict['loggers']['django'] = {
            'handlers': ['console', 'file'],
            'level': django_log_level,
            'propagate': False,
        }

        config_dict['loggers']['django.db.backends'] = {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if show_sql else django_log_level,
            'propagate': False,
        }

        return config_dict
