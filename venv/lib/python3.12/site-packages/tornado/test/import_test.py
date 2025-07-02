# flake8: noqa
import subprocess
import sys
import unittest

_import_everything = b"""
# The event loop is not fork-safe, and it's easy to initialize an asyncio.Future
# at startup, which in turn creates the default event loop and prevents forking.
# Explicitly disallow the default event loop so that an error will be raised
# if something tries to touch it.
import asyncio
asyncio.set_event_loop(None)

import tornado.auth
import tornado.autoreload
import tornado.concurrent
import tornado.escape
import tornado.gen
import tornado.http1connection
import tornado.httpclient
import tornado.httpserver
import tornado.httputil
import tornado.ioloop
import tornado.iostream
import tornado.locale
import tornado.log
import tornado.netutil
import tornado.options
import tornado.process
import tornado.simple_httpclient
import tornado.tcpserver
import tornado.tcpclient
import tornado.template
import tornado.testing
import tornado.util
import tornado.web
import tornado.websocket
import tornado.wsgi

try:
    import pycurl
except ImportError:
    pass
else:
    import tornado.curl_httpclient
"""


class ImportTest(unittest.TestCase):
    def test_import_everything(self):
        # Test that all Tornado modules can be imported without side effects,
        # specifically without initializing the default asyncio event loop.
        # Since we can't tell which modules may have already beein imported
        # in our process, do it in a subprocess for a clean slate.
        proc = subprocess.Popen([sys.executable], stdin=subprocess.PIPE)
        proc.communicate(_import_everything)
        self.assertEqual(proc.returncode, 0)

    def test_import_aliases(self):
        # Ensure we don't delete formerly-documented aliases accidentally.
        import tornado.ioloop
        import tornado.gen
        import tornado.util

        self.assertIs(tornado.ioloop.TimeoutError, tornado.util.TimeoutError)
        self.assertIs(tornado.gen.TimeoutError, tornado.util.TimeoutError)
