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
from twisted.web.client import URI, RedirectAgent, Agent, ProxyAgent, readBody
from twisted.web.http_headers import Headers


class CheckHttp:
    def setProp(self, ipAddr, hostname, url="/", port=80, timeout=5, ssl=False):
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
        self._follow = True
        self._response = dict()
        self._headers = Headers({b"User-Agent": [b"Zenoss HttpMonitor"]})

    def makeURL(self):
        url_data = URI.fromBytes(self._url)
        if not url_data.scheme:
            scheme = "https" if self._ssl else "http"
            self._reqURL = '{0}://{1}:{2}{3}'.format(scheme, self._hostname, self._port, self._url)
            return
        else:
            if url_data.host == self._hostname:
                scheme = "https" if self._ssl else "http"
                self._reqURL = '{0}://{1}:{2}{3}'.format(scheme, self._hostname, self._port, url_data.path)
                return
            else:
                self._proxyIp = self._ipAddr
                self._reqURL = '{0}://{1}:{2}{3}'.format(url_data.scheme, url_data.host, url_data.port, url_data.path)
                return

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
            endpoint = TCP4ClientEndpoint(self._reactor, self._ipAddr, self._port, self._port)
            agent = ProxyAgent(endpoint)
            agent = RedirectAgent(agent) if self._follow else agent
            return agent.request("GET", self._reqURL, self._headers)
        else:
            raise Exception("Can't choose a connection type")

    def _bodysize(self, body=""):
        return sys.getsizeof(body)

    def _noPage(self, ex):
        return ex

    def request(self, follow=True):
        self._follow = follow
        self._startTime = time.time()
        return self._agent().addCallbacks(self._getBody, self._noPage).addCallbacks(self._asnwer, self._noPage)

    def _getBody(self, response):
        self._response = response
        return readBody(response)

    def _asnwer(self, body):
        res = dict()
        res['body'] = body
        res['headers'] = self._response.headers
        res['code'] = self._response.code
        res['message'] = self._response.phrase
        res['time'] = time.time() - self._startTime
        res['size'] = self._bodysize(body)
        return res

