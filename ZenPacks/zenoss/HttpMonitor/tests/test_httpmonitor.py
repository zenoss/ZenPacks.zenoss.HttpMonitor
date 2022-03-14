##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018-2022, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from unittest import TestCase
from twisted.web.client import Agent
from ZenPacks.zenoss.HttpMonitor.http import HTTPMonitor, RedirectAgentZ
from ZenPacks.zenoss.HttpMonitor.datasources.HttpMonitorDataSource import HttpMonitorDataSourcePlugin
from ZenPacks.zenoss.HttpMonitor.tests import ModelTestCase

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

    def test_redirect_follow(self):
        location = "http://example.org/"
        hm = HTTPMonitor("10.20.30.40", "tester.test", "/path")
        hm._follow = "follow"
        hm._proxyIp = ""
        hm._hostnameIp.append("10.20.30.40")
        hm.makeURL()
        agent = RedirectAgentZ(Agent, onRedirect=hm._follow, port=hm._port, proxy=hm._proxyIp)
        self.assertEqual(agent._resolveLocation(hm._reqURL, location), "http://example.org/")

    def test_redirect_sticky(self):
        location = "http://example.org/"
        hm = HTTPMonitor("10.20.30.40", "tester.test", "/path")
        hm._follow = "sticky"
        hm._proxyIp = ""
        hm._hostnameIp.append("10.20.30.40")
        hm.makeURL()
        agent = RedirectAgentZ(Agent, onRedirect=hm._follow, port=hm._port, proxy=hm._proxyIp)
        self.assertEqual(agent._resolveLocation(hm._reqURL, location), "http://tester.test/")

    def test_redirect_stickyport(self):
        location = "http://example.org/"
        hm = HTTPMonitor("10.20.30.40", "tester.test", "/path", 8080)
        hm._follow = "stickyport"
        hm._proxyIp = ""
        hm._hostnameIp.append("10.20.30.40")
        hm.makeURL()
        agent = RedirectAgentZ(Agent, onRedirect=hm._follow, port=hm._port, proxy=hm._proxyIp)
        self.assertEqual(agent._resolveLocation(hm._reqURL, location), "http://example.org:8080/")

    def test_redirect_stickyport_443(self):
        location = "http://example.org/"
        hm = HTTPMonitor("10.20.30.40", "tester.test", "/path", 443)
        hm._follow = "stickyport"
        hm._proxyIp = ""
        hm._hostnameIp.append("10.20.30.40")
        hm.makeURL()
        agent = RedirectAgentZ(Agent, onRedirect=hm._follow, port=hm._port, proxy=hm._proxyIp)
        self.assertEqual(agent._resolveLocation(hm._reqURL, location), "http://example.org:443/")

    def test_redirect_stickyport_with_proxy(self):
        location = "http://example.org/"
        hm = HTTPMonitor("10.20.30.40", "tester.test", "http://tester.test:8888/path", 3128)
        hm._follow = "stickyport"
        hm._proxyIp = "10.10.10.10"
        hm._hostnameIp.append("10.20.30.50")
        hm.makeURL()
        agent = RedirectAgentZ(Agent, onRedirect=hm._follow, port=hm._port, proxy=hm._proxyIp)
        self.assertEqual(agent._resolveLocation(hm._reqURL, location), "http://example.org:8888/")

    def test_redirect_sticky_with_proxy(self):
        location = "http://example.org/"
        hm = HTTPMonitor("10.20.30.40", "tester.test", "http://tester.test:8888/path", 3128)
        hm._follow = "sticky"
        hm._proxyIp = "10.10.10.10"
        hm._hostnameIp.append("10.20.30.50")
        hm.makeURL()
        agent = RedirectAgentZ(Agent, onRedirect=hm._follow, port=hm._port, proxy=hm._proxyIp)
        self.assertEqual(agent._resolveLocation(hm._reqURL, location), "http://tester.test/")


class TestHttpMonitorDataSourcePlugin(ModelTestCase):

    def test_params(self):

        expected_params = {
            'basicAuthPass': '',
            'basicAuthUser': '',
            'caseSensitive': 'False',
            'eventClass': '/Status/HTTP',
            'eventKey': '',
            'hostname': 'http_device1',
            'invert': 'False',
            'ipAddress': '1.2.3.4',
            'onRedirect': 'follow',
            'port': '80',
            'proxyAuthPassword': '',
            'proxyAuthUser': '',
            'regex': '',
            'timeout': '60',
            'url': '/',
            'useSsl': 'False'
        }

        device_class = self.dmd.Devices.getOrganizer('/HTTP')
        device = device_class.createInstance(devId='http_device1')
        device.manageIp = '1.2.3.4'

        http_datasource = None

        templates = device.getRRDTemplates()
        for template in templates:
            if template.id == 'HttpMonitor':
                for datasource in template.datasources():
                    if datasource.id == 'HttpMonitor':
                        http_datasource = datasource

        if http_datasource:
            params = HttpMonitorDataSourcePlugin.params(http_datasource, device)
            self.assertEqual(params, expected_params)
