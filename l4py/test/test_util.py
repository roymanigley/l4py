import importlib
import logging
import logging.config
import os
from io import StringIO
from typing import Optional

from l4py import LogConfigBuilder, get_logger, utils
from l4py.builder import AbstractLoggingBuilder


def get_formatter_instance(logging_dict_config: dict, formatter_name: str) -> Optional[logging.Formatter]:
    if formatter := logging_dict_config['formatters'].get(formatter_name):
        if formatter_class := formatter.get('()'):
            formatter_module_class: str = formatter_class
            module_name = '.'.join(formatter_module_class.split('.')[:-1])
            class_name = formatter_module_class.split('.')[-1]
            module = importlib.import_module(module_name)
            return getattr(module, class_name)()
        if format := formatter.get('format'):
            return logging.Formatter(format)
    return None


def init_test_logger(
        builder: AbstractLoggingBuilder,
        logger_name: str = 'l4py.test.logger',
        handler_names: list[str] = None,
) -> tuple[logging.Logger, dict[str, StringIO]]:
    if handler_names is None:
        handler_names = ['console', 'file']

    config = builder.build_config()
    logging.config.dictConfig(config)
    logger = get_logger(logger_name)

    streams: dict[str: StringIO] = {}
    for handler_name in handler_names:
        stream = StringIO()
        streams[handler_name] = stream
        handler = logging.StreamHandler(stream)
        if formatter_instance := get_formatter_instance(config, handler_name):
            handler.setFormatter(formatter_instance)
            logger.addHandler(handler)

    return logger, streams


def l4py_entries_from_stream(stream: StringIO) -> list[str]:
    stream.seek(0)
    return stream.getvalue().split('\n')[:-1]


def l4py_test(
        *,
        builder: AbstractLoggingBuilder = LogConfigBuilder(),
        logger_name: str = 'l4py.test.logger',
        env_vars: dict[str, int] = None
):

    def decorator(function: callable):
        def wrapper(self):

            initial_vars = {}
            for key, value in os.environ.items():
                if key.startswith(utils.LOG_LEVEL_PREFIX):
                    initial_vars[key] = value
                    del os.environ[key]

            if env_vars:
                for key, value in env_vars.items():
                    os.environ.setdefault(key, str(value))

            handlers = []
            if builder.build_config()['handlers'].get('console'):
                handlers.append('console')
            if builder.build_config()['handlers'].get('file'):
                handlers.append('file')

            logger, streams = init_test_logger(
                builder=builder,
                logger_name=logger_name,
                handler_names=handlers,
            )
            try:
                function(self, logger, streams)
            except Exception as e:
                raise e
            finally:
                for key, value in initial_vars.items():
                    os.environ.setdefault(key, value)

        return wrapper

    return decorator
