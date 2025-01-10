# l4py
![Unit-Tests](https://github.com/roymanigley/l4py/actions/workflows/test.yml/badge.svg)  
![Published Python Package](https://github.com/roymanigley/l4py/actions/workflows/publish.yml/badge.svg)

> **`l4py`** is a Python library that simplifies logging configuration and enhances logging output with flexible formatting and output options. It offers an easy-to-use interface to configure both console and file logging with various customization features like JSON formatting, file rotation, and automatic log level handling. The library leverages the Python standard logging module and integrates seamlessly with Django's logging configuration.

## Key Features:
- **File Logging:** Automatically handles file logging with customizable file names, maximum size, and retention count.
- **JSON Support:** Optionally format log messages in JSON for structured output, both in console and log files.
- **Django Integration:** Simplifies Django logging configuration with a pre-built function to create a LOGGING dict compatible with Django's settings.
- **Customizable Logging Levels:** `l4py` allows you to define log levels using environment variables, following the pattern `L4PY_LOG_LEVEL_{logger_name}` and `L4PY_LOG_LEVEL_ROOT`. This enables dynamic configuration of log levels without the need to modify the code.
- **Utility Functions:** Includes utility functions for app name retrieval and platform-specific log file naming.

## Installation
```
pip install l4py
```
or from Github:
```
git clone https://github.com/roymanigley/l4py.git
cd l4py
pip install -r requirements.txt
python setup.py install
```
## Usage
> All th values set in the builder and the environment variables are the default values, and they don't have to be set explicit

```python
from l4py import LogConfigBuilder, get_logger, utils
import platform
import logging
import os

# Example of defining the loglevel using environment variables
os.environ.setdefault('L4PY_LOG_LEVEL_ROOT', 'INFO')
os.environ.setdefault('L4PY_LOG_LEVEL_module.class', 'INFO')

# Initializes the logging dict using `logging.config.dictConfig`
LogConfigBuilder()\
    .file(f'{utils.get_app_name()}-{platform.uname().node}.log')\
    .file_json(True)\
    .file_max_count(5)\
    .file_max_size_mb(5)\
    .console_json(False)\
    .init()

# returns a logger config dict
config_dict = LogConfigBuilder()\
    .file(f'{utils.get_app_name()}-{platform.uname().node}.log')\
    .file_json(True)\
    .file_max_count(5)\
    .file_max_size_mb(5)\
    .console_json(False)\
    .build_config_dict()

# Add this to you django `settings.py`
LOGGING = LogConfigBuilder()\
    .file(f'{utils.get_app_name()}-{platform.uname().node}.log')\
    .file_json(True)\
    .file_max_count(5)\
    .file_max_size_mb(5)\
    .console_json(False)\
    .build_config_dict_for_django(
        django_log_level=logging.INFO,
        show_sql=True
    )


logger = get_logger()

logger.debug('This is a DEBUG Message')
logger.info('This is a INFO Message')
logger.warning('This is a WARN Message')
logger.critical('This is a CRITICAL Message')
logger.fatal('This is a FATAL message')
```

With `l4py`, logging configuration becomes intuitive and consistent across different environments, making it a great choice for developers looking for a flexible and easy-to-integrate logging solution in Python applications.