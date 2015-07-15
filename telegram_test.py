import unittest

if __name__ == '__main__':
    testsuite = unittest.TestLoader().loadTestsFromTestCase(BotTest)
    unittest.TextTestRunner(verbosity=1).run(testsuite)
