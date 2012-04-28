try:
    import unittest2 as unittest
except ImportError:
    import unittest

import threading
import random as rnd
import time
from .util import get_test_conn
import eplasty as ep


class TestThread(threading.Thread):
    """Check if context is thread-locally isolated"""

    def __init__(self):
        self.conflicted = False
        super(TestThread, self).__init__()

    def run(self):
        for i in range(10):
            self.connection = get_test_conn()
            ep.set_context(self.connection)
            ep.start_session()
            self.session = ep.get_session()
            time.sleep(rnd.random() / 10)
            if self.session != ep.get_session():
                self.conflicted = True
                break


class Test(unittest.TestCase):

    def test_conflicts(self):
        threads = []
        for i in range(5):
            thread = TestThread()
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        for thread in threads:
            if thread.conflicted:
                raise AssertionError('Thread conflict!')


