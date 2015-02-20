# -*- coding: utf8 -*-

from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool

from noseapp.utils.runner import measure_time
from noseapp.runner.base import BaseTestRunner


def suite_wrapper(data):
    suite, result = data
    suite(result)


class ThreadsTestRunner(BaseTestRunner):
    """
    Run tests with multiprocessing.pool.ThreadPool
    """

    def run(self, suites):
        wrapper = self.config.plugins.prepareTest(suites)
        if wrapper is not None:
            suites = wrapper

        wrapped = self.config.plugins.setOutputStream(self.stream)
        if wrapped is not None:
            self.stream = wrapped

        result = self._makeResult()

        size = self.config.options.thread_pool
        if size < 0:
            size = cpu_count()

        pool = ThreadPool(size)

        with measure_time(result):
            pool.imap(suite_wrapper, ((suite, result) for suite in suites))
            pool.close()
            pool.join()

        self.config.plugins.finalize(result)
        return result
