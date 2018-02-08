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

from twisted.internet import reactor, ssl
from twisted.web.client import HTTPClientFactory


class CheckHttp(HTTPClientFactory):
    def __init__(self):
        self._url = None
        self.ipAddress = None
        self.deferred = None
        self._startTime = time.time()
        self._factory = None
        self._port = 80

    def makeURL(self, hostname, port=80, uri="/", useSsl=False):
        if useSsl:
            scheme = "https"
            port = 443
        else:
            scheme = "http"
        self._port = port
        url = scheme + '://' + hostname + ':' + str(port) + uri
        return url

    def seturl(self, url):
        self._url = url
        HTTPClientFactory.__init__(self, url=self._url)
        self.setURL(self._url)
        self._factory = self
        return self

    def setURL(self, url):
        HTTPClientFactory.setURL(self, url)
        self.path = url

    def page(self, page):
        if self.waiting:
            self.waiting = 0
            res = dict()
            res['body'] = page
            res['headers'] = self.response_headers
            res['code'] = self.status
            res['message'] = self.message
            res['time'] = time.time() - self._startTime
            res['size'] = self._bodysize(page)
            self.deferred.callback(res)

    def _bodysize(self, body=""):
        return sys.getsizeof(body)

    def noPage(self, reason):
        pass

    def useProxy(self, username, password):
        proxyAuth = base64.encodestring('%s:%s' % (username, password))
        proxy_authHeader = "Basic " + proxyAuth.strip()
        self.headers.update({'Proxy-Authorization': proxy_authHeader})

    def useAuth(self, username, password):
        basicAuth = base64.encodestring("%s:%s" % (username, password))
        authHeader = "Basic " + basicAuth.strip()
        AuthHeaders = {"Authorization": authHeader}
        self.headers.update(AuthHeaders)

    def processResult(self, response):
        return response

    @staticmethod
    def dealWithError(err):
        return err

    def connect(self):
        reactor.connectTCP(self.ipAddress, self._port, self._factory, self.timeout)
        self.deferred.addCallbacks(self.processResult, self.dealWithError)
        return self.deferred

    def connectssl(self):
        reactor.connectSSL(self.ipAddress, self._port, self._factory, ssl.ClientContextFactory(), self.timeout)
        self.deferred.addCallbacks(self.processResult, self.dealWithError)
        return self.deferred

    def setip(self, ip, timeout=30):
        self.ipAddress = ip
        self.timeout = timeout
