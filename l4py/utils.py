import logging
import os

LOG_LEVEL_PREFIX = 'L4PY_LOG_LEVEL_'
_LOG_LEVEL_ROOT_KEY = f'{LOG_LEVEL_PREFIX}ROOT'
_LOG_LEVEL_LOGGER_KEY_FORMAT = f'{LOG_LEVEL_PREFIX}{{}}'

_APP_NAME = 'python-app'


def set_app_name(app_name: str) -> None:
    global _APP_NAME
    _APP_NAME = app_name


def get_app_name() -> str:
    return os.environ.get('L4PY_APP_NAME', _APP_NAME)


def get_log_level_root_from_env() -> str or int:
    level = os.environ.get(_LOG_LEVEL_ROOT_KEY, f'{logging.INFO}')
    return int(level) if level.isdigit() else level


def get_log_levels_env() -> list[dict]:
    return [
        {'logger': key.replace(LOG_LEVEL_PREFIX, ''), 'level': int(
            value) if value.isdigit() else value}
        for key, value in os.environ.items()
        if key.startswith(LOG_LEVEL_PREFIX) and key != _LOG_LEVEL_ROOT_KEY
    ]
