##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import base64
import sys
import time

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.names import client, dns
from twisted.web.client import URI, RedirectAgent, Agent, ProxyAgent, readBody, PartialDownloadError
from twisted.web.http_headers import Headers


class CheckHttp:
    def _getIp(self, response):
        if response:
            for a in response[0]:
                if a.payload.TYPE == dns.A:
                    self._hostnameIp.append(a.payload.dottedQuad())
        return self.request()

    def setProp(self, ipAddr, hostname, url="/", port=80, timeout=5, ssl=False, follow=True):
        self._ipAddr = ipAddr
        self._port = port
        self._hostname = hostname
        self._url = url
        self._timeout = timeout
        self._ssl = ssl
        self._reactor = reactor
        self._clientEdnpoint = None
        self._proxyIp = None
        self._reqURL = ""
        self._startTime = None
        self._follow = follow
        self._response = dict()
        self._headers = Headers({b"User-Agent": [b"Zenoss HttpMonitor"]})
        self._body = ""
        self._hostnameIp = list()

    def makeURL(self):
        url_data = URI.fromBytes(self._url)
        if url_data.scheme:
            args = {
                "scheme": url_data.scheme,
                "host": url_data.host,
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
        self._reqURL = "{scheme}://{hostname}:{port}{path}".format(**args)
        url_data = URI.fromBytes(self._url)
        hasScheme = bool(url_data.scheme)
        hostMatch = url_data.host == self._hostname
        ipMatch = self._ipAddr in self._hostnameIp
        if (hasScheme and not hostMatch) or \
                (not hasScheme and xor(hostMatch, ipMatch)):
            self._proxyIp = self._ipAddr

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
            agent = RedirectAgent(agent) if self._follow else agent
            return agent.request("GET", self._reqURL, self._headers)
        elif self._proxyIp:
            endpoint = TCP4ClientEndpoint(reactor=self._reactor, host=self._ipAddr, port=self._port,
                                          timeout=self._timeout)
            agent = ProxyAgent(endpoint)
            agent = RedirectAgent(agent) if self._follow else agent
            return agent.request("GET", self._reqURL, self._headers)
        else:
            raise Exception("Can't choose a connection type")

    def _bodysize(self, body=""):
        return sys.getsizeof(body)

    def _pageErr(self, ex):
        if ex.type == PartialDownloadError:
            self._body = ex.value.response
            return
        return ex

    def connect(self):
        return client.lookupAddress(self._hostname).addCallbacks(self._getIp, self.request)

    def request(self):
        self.makeURL()
        self._startTime = time.time()
        return self._agent().addCallbacks(self._getBody, self._pageErr).addCallbacks(self._answer, self._pageErr)

    def _getBody(self, response):
        self._response = response
        return readBody(response).addErrback(self._pageErr)

    def _answer(self, body):
        res = dict()
        body = body if not self._body else self._body
        res['body'] = body
        res['headers'] = self._response.headers
        res['code'] = self._response.code
        res['message'] = self._response.phrase
        res['time'] = time.time() - self._startTime
        res['size'] = self._bodysize(body)
        return res

