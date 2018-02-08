##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2010, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


from Products.Zuul.interfaces import IRRDDataSourceInfo
from Products.Zuul.form import schema
from Products.Zuul.utils import ZuulMessageFactory as _t


class IHttpMonitorDataSourceInfo(IRRDDataSourceInfo):
    timeout = schema.Int(title=_t(u'Timeout (seconds)'))
    cycletime = schema.TextLine(title=_t(u'Cycle Time (seconds)'))
    hostname = schema.TextLine(title=_t(u'Host Name'), group=_t('HTTP Monitor'))
    port = schema.Int(title=_t(u'Port'), group=_t('HTTP Monitor'))
    ipAddress = schema.TextLine(title=_t(u'IP Address or Proxy Address'), group=_t('HTTP Monitor'))
    url = schema.TextLine(title=_t(u'URL'), group=_t('HTTP Monitor'))
    useSsl = schema.Bool(title=_t(u'Use SSL?'), group=_t('HTTP Monitor'))
    basicAuthUser = schema.TextLine(title=_t(u'Basic Auth User'), group=_t('HTTP Monitor'))
    basicAuthPass = schema.Password(title=_t(u'Basic Auth Password'), group=_t('HTTP Monitor'))
    onRedirect = schema.Choice(title=_t(u'Redirect Behavior'),
                             vocabulary='httpMonitorRedirectVocabulary', group=_t('HTTP Monitor'))
    proxyAuthUser = schema.TextLine(title=_t(u'Proxy User'), group=_t('Proxy Credentials'))
    proxyAuthPassword = schema.Password(title=_t(u'Proxy Password'), group=_t('Proxy Credentials'))
