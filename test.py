from l4py import LogConfigBuilder, get_logger


class Example4Logging:

    logger = get_logger()

    def do_some_logging(self):
        self.logger.debug('DEBUG message')
        self.logger.info('INFO message')
        self.logger.warning('WARN message')
        self.logger.critical('CRITICAL message')


if __name__ == '__main__':
    LogConfigBuilder().init()
    Example4Logging().do_some_logging()
