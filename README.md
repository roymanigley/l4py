# l4py
![Unit-Tests](https://github.com/roymanigley/l4py/actions/workflows/test.yml/badge.svg)  
![Published Python Package](https://github.com/roymanigley/l4py/actions/workflows/publish.yml/badge.svg)

```
██╗██╗  ██╗██████╗ ██╗   ██╗
██║██║  ██║██╔══██╗╚██╗ ██╔╝
██║███████║██████╔╝ ╚████╔╝ 
██║╚════██║██╔═══╝   ╚██╔╝  
███████╗██║██║        ██║   
╚══════╝╚═╝╚═╝        ╚═╝
```

> **`l4py`** is a Python library that simplifies logging configuration and enhances logging output with flexible formatting and output options. It offers an easy-to-use interface to configure both console and file logging with various customization features like JSON formatting, file rotation, and automatic log level handling. The library leverages the Python standard logging module and integrates seamlessly with Django's logging configuration.

## Key Features:
- **Context-aware Logging** (`trace_id` / `user_id`):** Automatically enriches all log records with `trace_id` and `user_id` when available in the active contextvars context.
- **File Logging:** Automatically handles file logging with customizable file names, maximum size, and retention count.
- **JSON Support:** Optionally format log messages in JSON for structured output, both in console and log files.
- **Django Integration:** Simplifies Django logging configuration with a pre-built function to create a LOGGING dict compatible with Django's settings.
- **Customizable Logging Levels:** `l4py` allows you to define log levels using environment variables, following the pattern `L4PY_LOG_LEVEL_{logger_name}` and `L4PY_LOG_LEVEL_ROOT`. This enables dynamic configuration of log levels without the need to modify the code.
- **Utility Functions:** Includes utility functions for app name retrieval and platform-specific log file naming.
- **Testing Support:** 
    - `@l4py_test` from `l4py.test` is a decorator to streamline testing and validation of logging behavior, ensuring precise control over loggers and outputs.
    - `l4py_entries_from_stream` from `l4py.test` is a helper function to extract and process log entries from streams for easy verification during tests.

### Example Code
![log code](https://github.com/roymanigley/l4py/raw/master/docs/img/l4py-poc.png)
### Default console output
![log output - console](https://github.com/roymanigley/l4py/raw/master/docs/img/l4py-output-console.png)
### Default file output
![log output - file](https://github.com/roymanigley/l4py/raw/master/docs/img/l4py-output-file.png)


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

**Environment Variables:**
- `L4PY_APP_NAME` default = 'python-app'
- `L4PY_LOG_LEVEL_{logger_name}` and `L4PY_LOG_LEVEL_ROOT`

```python
from l4py import LogConfigBuilder, LogConfigBuilderDjango, get_logger, utils
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
    .add_logger('my.logger', logging.DEBUG)\
    .init()

# returns a logger config dict
config_dict = LogConfigBuilder()\
    .file(f'{utils.get_app_name()}-{platform.uname().node}.log')\
    .file_json(True)\
    .file_max_count(5)\
    .file_max_size_mb(5)\
    .console_json(False)\
    .add_logger('my.logger', logging.DEBUG)\
    .build_config()

# Add this to you django `settings.py`
LOGGING = LogConfigBuilderDjango()\
    .django_log_level(logging.INFO)\
    .show_sql(False)\
    .add_logger('my.logger', logging.DEBUG)\
    .build_config()

logger = get_logger()

logger.debug('This is a DEBUG Message')
logger.info('This is a INFO Message')
logger.warning('This is a WARN Message')
logger.critical('This is a CRITICAL Message')
logger.fatal('This is a FATAL message')
```

### Set `trace_id` and `user_id`

#### Functions

```python
import uuid
from l4py.context import set_user_id, set_trace_id

set_trace_id(uuid.uuid4().hex)
set_user_id('royman')
```
#### Django Middleware
```python
import uuid
from django.utils.deprecation import MiddlewareMixin

from l4py.context import set_trace_id, set_user_id


class LoggingContextMiddleware(MiddlewareMixin):
    """
    Injects trace_id and user_id into contextvars for logging correlation.
    """

    def process_request(self, request):
        trace_id = request.headers.get("X-Trace-Id") or uuid.uuid4().hex
        set_trace_id(trace_id)

        user_id = None
        if hasattr(request, "user") and request.user.is_authenticated:
            user_id = str(request.user.id)
        set_user_id(user_id)

        request.trace_id = trace_id
        request.user_id = user_id

    def process_response(self, request, response):
        if hasattr(request, "trace_id"):
            response["X-Trace-Id"] = request.trace_id
        return response
```
#### Flask Request Hooks
```python
import uuid
from flask import request, g

from l4py.context import set_trace_id, set_user_id


def init_logging_context(app):

    @app.before_request
    def set_logging_context():
        trace_id = request.headers.get("X-Trace-Id") or uuid.uuid4().hex
        set_trace_id(trace_id)

        user_id = None
        if hasattr(g, "user") and getattr(g.user, "is_authenticated", False):
            user_id = str(g.user.id)
        set_user_id(user_id)

        g.trace_id = trace_id
        g.user_id = user_id

    @app.after_request
    def attach_trace_id_to_response(response):
        if hasattr(g, "trace_id"):
            response.headers["X-Trace-Id"] = g.trace_id
        return response
```

## Testing

```python
import json
import logging
import unittest

from l4py import LogConfigBuilder, utils
from l4py.test import l4py_test, l4py_entries_from_stream


class LoggerTest(unittest.TestCase):
    
    @l4py_test(
        env_vars={
            f'{utils.LOG_LEVEL_PREFIX}parent': logging.DEBUG,
            f'{utils.LOG_LEVEL_PREFIX}parent.child': logging.WARNING
        }, # optional,
        logger_name='parent', # optional
        builder=LogConfigBuilder(), # optional
    )
    def test_setting_parent_level__should_log_all_from_parent_but_only_warning_from_child(
            self,
            parent_logger: logging.Logger,
            streams
    ):
        # WHEN
        child_logger = logging.getLogger('parent.child')

        child_logger.critical('This is a CRITICAL Message from the child Logger')
        child_logger.warning('This is a WARN Message from the child Logger')
        child_logger.info('This is a INFO Message from the child Logger')
        child_logger.info('This is a DEBUG Message from the child Logger')

        parent_logger.critical('This is a CRITICAL Message from the parent Logger')
        parent_logger.warning('This is a WARN Message from the parent Logger')
        parent_logger.info('This is a INFO Message from the parent Logger')
        parent_logger.debug('This is a DEBUG Message from the parent Logger')

        # THEN
        console_entries = l4py_entries_from_stream(streams['console'])
        file_entries = l4py_entries_from_stream(streams['file'])

        [print(e) for e in console_entries]
        self.assertEqual(len(console_entries), 6)
        self.assertEqual(len(file_entries), 6)

        self.assertRegex(console_entries[0], r'^.+\[CRITICAL\].+from the child Logger')
        self.assertRegex(console_entries[1], r'^.+\[WARNING \].+from the child Logger')
        self.assertRegex(console_entries[2], r'^.+\[CRITICAL\].+from the parent Logger')
        self.assertRegex(console_entries[3], r'^.+\[WARNING \].+from the parent Logger')
        self.assertRegex(console_entries[4], r'^.+\[INFO    \].+from the parent Logger')
        self.assertRegex(console_entries[5], r'^.+\[DEBUG   \].+from the parent Logger')

        self.assertEqual(json.loads(file_entries[0])['level'], 'CRITICAL')
        self.assertEqual(json.loads(file_entries[0])['message'], 'This is a CRITICAL Message from the child Logger')
        self.assertEqual(json.loads(file_entries[1])['level'], 'WARNING')
        self.assertEqual(json.loads(file_entries[1])['message'], 'This is a WARN Message from the child Logger')
        self.assertEqual(json.loads(file_entries[2])['level'], 'CRITICAL')
        self.assertEqual(json.loads(file_entries[2])['message'], 'This is a CRITICAL Message from the parent Logger')
        self.assertEqual(json.loads(file_entries[3])['level'], 'WARNING')
        self.assertEqual(json.loads(file_entries[3])['message'], 'This is a WARN Message from the parent Logger')
        self.assertEqual(json.loads(file_entries[4])['level'], 'INFO')
        self.assertEqual(json.loads(file_entries[4])['message'], 'This is a INFO Message from the parent Logger')
        self.assertEqual(json.loads(file_entries[5])['level'], 'DEBUG')
        self.assertEqual(json.loads(file_entries[5])['message'], 'This is a DEBUG Message from the parent Logger')
```

# ToDo

- [ ] Extend the tests
    - [ ] format
    - [ ] formatter
    - [ ] filters
    - [ ] disable handlers (`console`, `file`)
    - [ ] log file
      

With `l4py`, logging configuration becomes intuitive and consistent across different environments, making it a great choice for developers looking for a flexible and easy-to-integrate logging solution in Python applications.
