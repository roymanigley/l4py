import json
import logging
import unittest
from io import StringIO

from l4py import LogConfigBuilder
from l4py import utils
from l4py.test import l4py_test, l4py_entries_from_stream


class LoggerTest(unittest.TestCase):

    @l4py_test(
        env_vars={f'{utils.LOG_LEVEL_PREFIX}ROOT': logging.CRITICAL},
    )
    def test_setting_root_level__should_only_log_fatal(self, logger: logging.Logger, streams):
        # WHEN
        logger.critical('This is a CRITICAL Message')
        logger.warning('This is a WARN Message')
        logger.info('This is a INFO Message')
        logger.debug('This is a DEBUG Message')

        # THEN
        console_entries = l4py_entries_from_stream(streams['console'])
        file_entries = l4py_entries_from_stream(streams['file'])

        self.assertEqual(len(console_entries), 1)
        self.assertEqual(len(file_entries), 1)

        self.assertRegex(console_entries[0], r'^.+\[CRITICAL\].+')
        self.assertEqual(json.loads(file_entries[0])['level'], 'CRITICAL')

    @l4py_test(
        env_vars={
            f'{utils.LOG_LEVEL_PREFIX}parent': logging.DEBUG,
            f'{utils.LOG_LEVEL_PREFIX}parent.child': logging.WARNING
        },
        logger_name='parent',
        builder=LogConfigBuilder()
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


    @l4py_test(
        builder=LogConfigBuilder()
    )
    def test_exception_logging(self, logger: logging.Logger, streams: list[StringIO]):
        try:
            1/0
        except ZeroDivisionError:
            logger.exception('Hello')

        exception_message = ' '.join(l4py_entries_from_stream(streams['console']))

        self.assertRegex(exception_message, '^.+Traceback.+1/0.+ZeroDivisionError: division by zero.+')


if __name__ == '__main__':
    unittest.main()
