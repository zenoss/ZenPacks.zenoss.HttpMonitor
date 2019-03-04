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
from twisted.internet import reactor, ssl
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.names import client, error, dns
from twisted.python.failure import Failure
from twisted.web.client import (
    URI, RedirectAgent, Agent, ProxyAgent, readBody, PartialDownloadError, Response
)
from twisted.web.iweb import IPolicyForHTTPS
from twisted.web.http_headers import Headers
from zope.interface import implementer

log = logging.getLogger('zen.HttpMonitor')

@implementer(IPolicyForHTTPS)
class NoVerifyContextFactory(object):
    def creatorForNetloc(self, hostname, port):
        return ssl.CertificateOptions(verify=False)

class RedirectAgentZ(RedirectAgent):
    def __init__(self, agent, onRedirect, port=80, proxy=""):
        RedirectAgent.__init__(self, agent, 20)
        self._onRedirect = onRedirect
        self._port = port
        self._proxy = proxy

    def _resolveLocation(self, requestURI, location):
        from twisted.web.client import _urljoin
        from urlparse import urlparse, urlsplit
        old_url = urlsplit(requestURI)[1].split(":")
        go_to = urlsplit(location)[1].split(":")

        if self._onRedirect == "sticky":
            location = location.replace(go_to[0], old_url[0])
        elif self._onRedirect == "stickyport":
            def _preparePort(url):
                urlsplited = urlsplit(url)[1].split(":")
                scheme = urlsplit(url).scheme \
                    if urlsplit(url).scheme else "http"
                if scheme == "http":
                    url = url.replace(urlsplited[0], urlsplited[0]+":80")
                elif scheme == "https":
                    url = url.replace(urlsplited[0], urlsplited[0]+":443")
                return url

            if len(old_url) != 2:
                requestURI = _preparePort(requestURI)
                old_url = urlsplit(requestURI)[1].split(":")
            if len(go_to) != 2:
                location = _preparePort(location)
                go_to = urlsplit(location)[1].split(":")
            if not self._proxy:
                location = location.replace(go_to[1], str(self._port))
            else:
                location = location.replace(go_to[1], old_url[1])
        location = _urljoin(requestURI, location)
        log.debug("Locating to URL: %s" % location)
        return location

    def _handleRedirect(self, response, method, uri, headers, redirectCount):
        """
        Handle a redirect response, checking the number of redirects already
        followed, and extracting the location header fields.
        """
        if redirectCount >= self._redirectLimit:
            err = error.InfiniteRedirection(
                response.code,
                b'Infinite redirection detected',
                location=uri)
            raise ResponseFailed([Failure(err)], response)
        locationHeaders = response.headers.getRawHeaders(b'location', [])
        if not locationHeaders:
            err = error.RedirectWithNoLocation(
                response.code, b'No location header field', uri)
            raise ResponseFailed([Failure(err)], response)
        # ZPS-4904
        location = self._resolveLocation(
            response.request.absoluteURI, locationHeaders[0])
        deferred = self._agent.request(method, location, headers)
        def _chainResponse(newResponse):
            newResponse.setPreviousResponse(response)
            return newResponse
        deferred.addCallback(_chainResponse)
        return deferred.addCallback(
            self._handleResponse, method, uri, headers, redirectCount + 1)

class HTTPMonitor:
    def __init__(
            self, ipAddr, hostname,
            url="/", port=80, timeout=5, ssl=False, follow="ok"):
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
        portProtoMatch = self._ssl and int(args['port']) == 443 or \
                            not self._ssl and int(args['port']) == 80
        if hasHost and xor(hostMatch, ipMatch) or not ipMatch:
            self._proxyIp = self._ipAddr
        # Remove port if default (see RFC 2616, 14.23)
        if (int(args['port']) in (80, 443) and portProtoMatch) or \
                bool(self._proxyIp) and not url_data.scheme:
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
            agent = Agent(self._reactor, contextFactory=NoVerifyContextFactory(),
                            connectTimeout=self._timeout)
        else:
            endpoint = TCP4ClientEndpoint(
                reactor=self._reactor, host=self._ipAddr, port=self._port,
                timeout=self._timeout
            )
            agent = ProxyAgent(endpoint)
        if self._follow in ('follow', 'sticky', 'stickyport'):
            agent = RedirectAgentZ(
                agent, onRedirect=self._follow, port=self._port, proxy=self._proxyIp
            )
        return agent.request("GET", self._reqURL, self._headers)

    def _bodysize(self, body="", response=""):
        headers_len = 0
        if isinstance(response, Response):
            headers = response.headers.getAllRawHeaders()
            for k, v in headers:
                headers_len += len(k+": ") + len(v[0]+"\r\n")
        return len(body)+headers_len

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
        if self._ipAddr and not isip(self._ipAddr):
            return client.lookupAddress(self._ipAddr).addCallbacks(
                self._lookupProxyIp, self._lookupProxyIpErr
            )
        if self._hostname and not isip(self._hostname):
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

        if self._follow == "fail":
            if self._response.code in (301,302,303,307,308):
                res['msg'] = {'status': 'CRITICAL', 'msg': ''}

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
