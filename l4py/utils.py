import logging
import os

_LOG_LEVEL_PREFIX = 'L4PY_LOG_LEVEL_'
_LOG_LEVEL_ROOT_KEY = f'{_LOG_LEVEL_PREFIX}ROOT'
_LOG_LEVEL_LOGGER_KEY_FORMAT = f'{_LOG_LEVEL_PREFIX}{{}}'


def get_app_name() -> str:
    return os.environ.get('L4PY_APP_NAME', 'python-app')


def get_log_level_root() -> str:
    return os.environ.get(_LOG_LEVEL_ROOT_KEY, logging.INFO)


def get_log_levels_env() -> list[dict]:
    return [
        {'logger': key.replace(_LOG_LEVEL_PREFIX, ''), 'level': value}
        for key, value in os.environ.items()
        if key.startswith(_LOG_LEVEL_PREFIX)
    ]
