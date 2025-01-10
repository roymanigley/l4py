import unittest

from l4py import LogConfigBuilder, get_logger


class LoggerTest(unittest.TestCase):

    def test(self):
        LogConfigBuilder().init()
        logger = get_logger()

        logger.debug('This is a DEBUG Message')
        logger.info('This is a INFO Message')
        logger.warning('This is a WARN Message')
        logger.critical('This is a CRITICAL Message')
        logger.fatal('This is a FATAL message')


if __name__ == '__main__':
    unittest.main()
