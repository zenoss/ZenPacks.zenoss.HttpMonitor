###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2010, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.template import RRDDataSourceInfo
from ZenPacks.zenoss.HttpMonitor.interfaces import IHttpMonitorDataSourceInfo
from ZenPacks.zenoss.HttpMonitor.datasources.HttpMonitorDataSource import HttpMonitorDataSource

def httpMonitorRedirectVocabulary(context):
    return SimpleVocabulary.fromValues(HttpMonitorDataSource.onRedirectOptions)


class HttpMonitorDataSourceInfo(RRDDataSourceInfo):
    implements(IHttpMonitorDataSourceInfo)
    timeout = ProxyProperty('timeout')
    cycletime = ProxyProperty('cycletime')
    hostname = ProxyProperty('hostname')
    ipAddress = ProxyProperty('ipAddress')
    port = ProxyProperty('port')
    useSsl = ProxyProperty('useSsl')
    url = ProxyProperty('url')
    regex = ProxyProperty('regex')
    caseSensitive = ProxyProperty('caseSensitive')
    invert = ProxyProperty('invert')
    basicAuthUser = ProxyProperty('basicAuthUser')
    basicAuthPass = ProxyProperty('basicAuthPass')
    onRedirect = ProxyProperty('onRedirect')
    
    @property
    def testable(self):
        """
        We can NOT test this datsource against a specific device
        """
        return False
    


