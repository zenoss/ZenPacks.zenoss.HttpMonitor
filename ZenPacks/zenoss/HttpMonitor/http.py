##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import base64
import logging
import sys
import time
from operator import xor

from Products.ZenUtils.IpUtil import isip
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.names import client, error, dns
from twisted.python.failure import Failure
from twisted.web.client import (
    URI, RedirectAgent, Agent, ProxyAgent, readBody, PartialDownloadError, Response
)
from twisted.web.http_headers import Headers

log = logging.getLogger('zen.HttpMonitor')


class HTTPMonitor:
    def __init__(
            self, ipAddr, hostname,
            url="/", port=80, timeout=5, ssl=False, follow=True):
        self._ipAddr = ipAddr
        self._port = port
        self._hostname = hostname
        self._url = url
        self._timeout = timeout
        self._ssl = ssl
        self._reactor = reactor
        self._proxyIp = None
        self._reqURL = ""
        self._startTime = None
        self._follow = follow
        self._response = dict()
        self._headers = Headers({b"User-Agent": [b"Zenoss HttpMonitor"]})
        self._body = ""
        self._hostnameIp = list()
        self._regex = ""
        self._caseSensitive = False
        self._invert = False


    def _getIp(self, response):
        if response:
            for a in response[0]:
                if a.payload.TYPE == dns.A:
                    self._hostnameIp.append(a.payload.dottedQuad())
        return self.request()

    def makeURL(self):
        url_data = URI.fromBytes(self._url)
        if url_data.scheme:
            args = {
                "scheme": url_data.scheme,
                "hostname": url_data.host,
                "port": url_data.port,
                "path": url_data.path,
            }
        else:
            args = {
                "scheme": "https" if self._ssl else "http",
                "hostname": self._hostname,
                "port": self._port,
                "path": self._url,
            }
        hasHost = bool(url_data.host)
        hostMatch = url_data.host.endswith(self._hostname)
        ipMatch = self._ipAddr in self._hostnameIp
        if hasHost and xor(hostMatch, ipMatch) or not ipMatch:
            self._proxyIp = self._ipAddr
        # Remove port if default (see RFC 2616, 14.23)
        if int(args['port']) in (80, 443) or \
                self._proxyIp and not url_data.scheme:
            self._reqURL = "{scheme}://{hostname}{path}".format(**args)
        else:
            self._reqURL = "{scheme}://{hostname}:{port}{path}".format(**args)
        log.debug(
            "HTTP request URL: %s, Proxy: %s", self._reqURL, self._proxyIp
        )

    def useProxy(self, username, password):
        proxyAuth = base64.encodestring('%s:%s' % (username, password))
        proxy_authHeader = "Basic " + proxyAuth.strip()
        self._headers.setRawHeaders('Proxy-Authorization', [proxy_authHeader])

    def useAuth(self, username, password):
        basicAuth = base64.encodestring("%s:%s" % (username, password))
        authHeader = "Basic " + basicAuth.strip()
        self._headers.setRawHeaders("Authorization", [authHeader])

    def _agent(self):
        if not self._proxyIp:
            agent = Agent(self._reactor, connectTimeout=self._timeout)
        else:
            endpoint = TCP4ClientEndpoint(
                reactor=self._reactor, host=self._ipAddr, port=self._port,
                timeout=self._timeout
            )
            agent = ProxyAgent(endpoint)
        agent = RedirectAgent(agent) if self._follow else agent
        return agent.request("GET", self._reqURL, self._headers)

    def _bodysize(self, body="", response=""):
        heades_len = 0
        if isinstance(response, Response):
            headers = response.headers.getAllRawHeaders()
            for k, v in headers:
                heades_len += len(k+": ") + len(v[0]+"\r\n")
        return len(body)+heades_len

    def _pageErr(self, failure):
        if failure.type == PartialDownloadError:
            self._body = failure.value.response
            return
        return failure

    def _lookupErr(self, failure):
        ex = failure.check(error.DNSNameError)
        if ex:
            # The message of a DNS exception is not useful, so create an
            # exception with a useful message and return that instead.
            return Failure(
                exc_value=RuntimeError("hostname not found"),
                exc_type=RuntimeError,
                exc_tb=failure.tb,
                captureVars=failure.captureVars
            )
        return failure

    def _lookupProxyIpErr(self, failure):
        return Failure(
            exc_value=RuntimeError("Unable to resolve hostname (%s) as IP address" % (self._ipAddr)),
            exc_type=RuntimeError
            )

    def _lookupProxyIp(self, response):
        if response:
            for a in response[0]:
                if a.payload.TYPE == dns.A:
                    self._ipAddr = a.payload.dottedQuad()
                    break
        return self.connect()

    def connect(self):
        if not isip(self._ipAddr):
            return client.lookupAddress(self._ipAddr).addCallbacks(
                self._lookupProxyIp, self._lookupProxyIpErr
            )
        if not isip(self._hostname):
            return client.lookupAddress(self._hostname).addCallbacks(
                self._getIp, self._lookupErr
            )
        return self.request()

    def request(self):
        self.makeURL()
        self._startTime = time.time()
        return self._agent().addCallbacks(
            self._getBody, self._pageErr
        ).addCallbacks(self._answer, self._pageErr)

    def _getBody(self, response):
        self._response = response
        return readBody(response).addErrback(self._pageErr)

    def _answer(self, body=""):
        res = dict()
        body = str(body if not self._body else self._body)
        res['body'] = body
        res['headers'] = self._response.headers
        res['code'] = self._response.code
        res['message'] = self._response.phrase
        res['time'] = time.time() - self._startTime
        res['size'] = self._bodysize(body, self._response)
        if self._regex:
            regex = self._checkRegex(body)
            if regex and regex.get('status', ""):
                res['msg'] = regex
        return res

    def regex(self, regex, caseSensitive=False, invert=False):
        self._regex = regex
        self._caseSensitive = caseSensitive
        self._invert = invert

    def _checkRegex(self, body=""):
        import re
        try:
            if self._caseSensitive:
                regex = re.compile(self._regex)
            else:
                regex = re.compile(self._regex, re.IGNORECASE)
        except re.error as err:
            return {'status': 'CRITICAL', 'msg': 'Could not compile regular expression: '+
                    repr(self._regex)}

        match = bool(regex.search(body))
        if (not match and not self._invert) or (match and self._invert):
            if self._invert:
                return {'status': 'CRITICAL', 'msg': 'pattern found'}
            else:
                return {'status': 'CRITICAL', 'msg': 'pattern not found'}
