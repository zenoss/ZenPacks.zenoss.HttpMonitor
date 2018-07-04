##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from unittest import TestCase

from ZenPacks.zenoss.HttpMonitor.http import HTTPMonitor

# ipAddr, hostname, url="/", port=80, timeout=5, ssl=False, follow=True):


class TestHttpMonitor(TestCase):

    def test_noproxy_nourl(self):
        hm = HTTPMonitor("192.168.20.100", "tester.test")
        hm._hostnameIp.append("192.168.20.100")
        hm.makeURL()
        self.assertEqual(hm._reqURL, "http://tester.test/")
        self.assertIsNone(hm._proxyIp)

    def test_noproxy_nourl_nondefault_port(self):
        hm = HTTPMonitor("192.168.20.100", "tester.test", port=8050)
        hm._hostnameIp.append("192.168.20.100")
        hm.makeURL()
        self.assertEqual(hm._reqURL, "http://tester.test:8050/")
        self.assertIsNone(hm._proxyIp)

    def test_noproxy_withurl(self):
        hm = HTTPMonitor(
            "192.168.20.100", "tester.test", "http://www.tester.test"
        )
        hm._hostnameIp.append("192.168.20.100")
        hm.makeURL()
        self.assertEqual(hm._reqURL, "http://www.tester.test")
        self.assertIsNone(hm._proxyIp)

    def test_noproxy_url_has_default_port(self):
        hm = HTTPMonitor(
            "192.168.20.100", "tester.test", "http://www.tester.test:80"
        )
        hm._hostnameIp.append("192.168.20.100")
        hm.makeURL()
        self.assertEqual(hm._reqURL, "http://www.tester.test")
        self.assertIsNone(hm._proxyIp)

    def test_noproxy_url_default_port_with_path(self):
        hm = HTTPMonitor(
            "192.168.20.100", "tester.test", "http://www.tester.test:80/path"
        )
        hm._hostnameIp.append("192.168.20.100")
        hm.makeURL()
        self.assertEqual(hm._reqURL, "http://www.tester.test/path")
        self.assertIsNone(hm._proxyIp)

    def test_noproxy_url_nondefault_port(self):
        hm = HTTPMonitor(
            "192.168.20.100", "tester.test", "http://www.tester.test:8050"
        )
        hm._hostnameIp.append("192.168.20.100")
        hm.makeURL()
        self.assertEqual(hm._reqURL, "http://www.tester.test:8050")
        self.assertIsNone(hm._proxyIp)

    def test_noproxy_pathonlyurl(self):
        hm = HTTPMonitor(
            "192.168.20.100", "tester.test", "/path"
        )
        hm._hostnameIp.append("192.168.20.100")
        hm.makeURL()
        self.assertEqual(hm._reqURL, "http://tester.test/path")
        self.assertIsNone(hm._proxyIp)

    def test_proxy_nourl(self):
        hm = HTTPMonitor("10.20.30.40", "tester.test")
        hm._hostnameIp.append("192.168.20.100")
        hm.makeURL()
        self.assertEqual(hm._reqURL, "http://tester.test/")
        self.assertEqual(hm._proxyIp, "10.20.30.40")

    def test_proxy_nourl_nondefault_port(self):
        hm = HTTPMonitor("10.20.30.40", "tester.test", port=8050)
        hm._hostnameIp.append("192.168.20.100")
        hm.makeURL()
        self.assertEqual(hm._reqURL, "http://tester.test/")
        self.assertEqual(hm._proxyIp, "10.20.30.40")

    def test_proxy_withurl(self):
        hm = HTTPMonitor(
            "10.20.30.40", "tester.test", "http://www.tester.test"
        )
        hm._hostnameIp.append("192.168.20.100")
        hm.makeURL()
        self.assertEqual(hm._reqURL, "http://www.tester.test")
        self.assertEqual(hm._proxyIp, "10.20.30.40")

    def test_proxy_url_has_default_port(self):
        hm = HTTPMonitor(
            "10.20.30.40", "tester.test", "http://www.tester.test:80"
        )
        hm._hostnameIp.append("192.168.20.100")
        hm.makeURL()
        self.assertEqual(hm._reqURL, "http://www.tester.test")
        self.assertEqual(hm._proxyIp, "10.20.30.40")

    def test_proxy_url_default_port_with_path(self):
        hm = HTTPMonitor(
            "10.20.30.40", "tester.test", "http://www.tester.test:80/path"
        )
        hm._hostnameIp.append("192.168.20.100")
        hm.makeURL()
        self.assertEqual(hm._reqURL, "http://www.tester.test/path")
        self.assertEqual(hm._proxyIp, "10.20.30.40")

    def test_proxy_url_nondefault_port(self):
        hm = HTTPMonitor(
            "10.20.30.40", "tester.test", "http://www.tester.test:8050"
        )
        hm._hostnameIp.append("192.168.20.100")
        hm.makeURL()
        self.assertEqual(hm._reqURL, "http://www.tester.test:8050")
        self.assertEqual(hm._proxyIp, "10.20.30.40")

    def test_proxyport_url_nondefault_port(self):
        hm = HTTPMonitor(
            "10.20.30.40", "tester.test", "http://www.tester.test:8050",
            port=6000
        )
        hm._hostnameIp.append("192.168.20.100")
        hm.makeURL()
        self.assertEqual(hm._reqURL, "http://www.tester.test:8050")
        self.assertEqual(hm._proxyIp, "10.20.30.40")
        self.assertEqual(hm._port, 6000)

    def test_proxy_pathonlyurl(self):
        hm = HTTPMonitor("10.20.30.40", "tester.test", "/path")
        hm._hostnameIp.append("192.168.20.100")
        hm.makeURL()
        self.assertEqual(hm._reqURL, "http://tester.test/path")
        self.assertEqual(hm._proxyIp, "10.20.30.40")

    def test_regex_not_found(self):
        body = "Hello Web!"
        hm = HTTPMonitor("10.20.30.40", "tester.test", "/path")
        hm.regex("test", caseSensitive=False, invert=False)
        self.assertEqual(hm._checkRegex(body), {'status': 'CRITICAL', 'msg': 'pattern not found'})

    def test_regex_found(self):
        body = "Hello Web!"
        hm = HTTPMonitor("10.20.30.40", "tester.test", "/path")
        hm.regex("Web", caseSensitive=False, invert=False)
        self.assertEqual(hm._checkRegex(body), None)

    def test_regex_invert(self):
        body = "Hello Web!"
        hm = HTTPMonitor("10.20.30.40", "tester.test", "/path")
        hm.regex("NotFound", caseSensitive=False, invert=True)
        self.assertEqual(hm._checkRegex(body), None)

    def test_regex_caseSensitive(self):
        body = "Hello Web!"
        hm = HTTPMonitor("10.20.30.40", "tester.test", "/path")
        hm.regex("hello", caseSensitive=True, invert=False)
        self.assertEqual(hm._checkRegex(body), {'status': 'CRITICAL', 'msg': 'pattern not found'})

    def test_regex_caseSensitive_invert(self):
        body = "Hello Web!"
        hm = HTTPMonitor("10.20.30.40", "tester.test", "/path")
        hm.regex("hello", caseSensitive=True, invert=True)
        self.assertEqual(hm._checkRegex(body), None)

    def test_regex_wrong_expression(self):
        body = "Hello Web!"
        hm = HTTPMonitor("10.20.30.40", "tester.test", "/path")
        hm.regex("[]*", caseSensitive=False, invert=False)
        self.assertEqual(hm._checkRegex(body), {'status': 'CRITICAL',
                                                'msg': "Could not compile regular expression: '[]*'"})
