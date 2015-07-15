import unittest
from tests.test_bot import BotTest

if __name__ == '__main__':
    testsuite = unittest.TestLoader().loadTestsFromTestCase(BotTest)
    unittest.TextTestRunner(verbosity=1).run(testsuite)
