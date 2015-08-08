import logging
import unittest
from tests.test_bot import BotTest

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    testsuite = unittest.TestLoader().loadTestsFromTestCase(BotTest)
    unittest.TextTestRunner(verbosity=1).run(testsuite)
