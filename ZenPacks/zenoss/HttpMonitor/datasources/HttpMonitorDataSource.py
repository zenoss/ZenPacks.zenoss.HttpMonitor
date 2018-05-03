##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################


__doc__ = '''HttpMonitorDataSource.py

Defines datasource for HttpMonitor
'''

from Products.ZenEvents import ZenEventClasses
from ZenPacks.zenoss.HttpMonitor.http import CheckHttp

from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.template import RRDDataSourceInfo
from Products.Zuul.interfaces import IRRDDataSourceInfo
from Products.Zuul.utils import ZuulMessageFactory as _t

from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource \
    import PythonDataSource, PythonDataSourcePlugin

import ast
import logging

log = logging.getLogger('zen.HttpMonitor')


class HttpMonitorDataSource(PythonDataSource):
    HTTP_MONITOR = 'HttpMonitor'
    ZENPACKID = 'ZenPacks.zenoss.HttpMonitor'
    sourcetypes = (HTTP_MONITOR,)
    sourcetype = HTTP_MONITOR
    plugin_classname = (
            ZENPACKID + '.datasources.HttpMonitorDataSource.HttpMonitorDataSourcePlugin')
    timeout = 60
    eventClass = '/Status/Web'

    hostname = '${dev/id}'
    ipAddress = '${dev/manageIp}'
    port = 80
    useSsl = False
    url = '/'
    basicAuthUser = ''
    basicAuthPass = ''
    onRedirect = True
    proxyAuthUser = ''
    proxyAuthPassword = ''
    _properties = PythonDataSource._properties + (
        {'id': 'hostname', 'type': 'string', 'mode': 'w'},
        {'id': 'ipAddress', 'type': 'string', 'mode': 'w'},
        {'id': 'port', 'type': 'int', 'mode': 'w'},
        {'id': 'useSsl', 'type': 'boolean', 'mode': 'w'},
        {'id': 'url', 'type': 'string', 'mode': 'w'},
        {'id': 'basicAuthUser', 'type': 'string', 'mode': 'w'},
        {'id': 'basicAuthPass', 'type': 'string', 'mode': 'w'},
        {'id': 'onRedirect', 'type': 'boolean', 'mode': 'w'},
        {'id': 'timeout', 'type': 'int', 'mode': 'w'},
        {'id': 'proxyAuthUser', 'type': 'string', 'mode': 'w'},
        {'id': 'proxyAuthPassword', 'type': 'string', 'mode': 'w'},
    )


class HttpMonitorDataSourcePlugin(PythonDataSourcePlugin):

    @classmethod
    def params(cls, datasource, context):
        params = dict()

        params['hostname'] = datasource.talesEval(
            datasource.hostname, context)

        params['ipAddress'] = datasource.talesEval(
            datasource.ipAddress, context)

        params['port'] = datasource.talesEval(
            datasource.port, context)

        params['useSsl'] = datasource.talesEval(
            datasource.useSsl, context)

        params['url'] = datasource.talesEval(
            datasource.url, context)

        params['basicAuthUser'] = datasource.talesEval(
            datasource.basicAuthUser, context)

        params['basicAuthPass'] = datasource.talesEval(
            datasource.basicAuthPass, context)

        params['onRedirect'] = datasource.talesEval(
            datasource.onRedirect, context)

        params['proxyAuthUser'] = datasource.talesEval(
            datasource.proxyAuthUser, context)

        params['proxyAuthPassword'] = datasource.talesEval(
            datasource.proxyAuthPassword, context)

        params['eventKey'] = datasource.talesEval(
            datasource.eventKey, context)

        params['eventClass'] = datasource.talesEval(
            datasource.eventClass, context)

        params['timeout'] = datasource.talesEval(
            datasource.timeout, context)

        return params

    def collect(self, config):
        log.info("HTTPMonitor collecting started")
        ds0 = config.datasources[0]
        hostname = ds0.params['hostname']
        timeout = int(ds0.params['timeout'])
        port = int(ds0.params['port'])
        useSsl = ast.literal_eval(ds0.params['useSsl'])
        url = ds0.params['url']
        ipaddress = ds0.params['ipAddress']
        onRedirect = ast.literal_eval(ds0.params['onRedirect'])
        basicAuthUser = ds0.params['basicAuthUser']
        basicAuthPass = ds0.params['basicAuthPass']
        proxyAuthUser = ds0.params['proxyAuthUser']
        proxyAuthPassword = ds0.params['proxyAuthPassword']
        chttp = CheckHttp()
        chttp.setProp(ipAddr=ipaddress, hostname=hostname, url=url, port=port, timeout=timeout, ssl=useSsl)
        chttp.makeURL()
        if proxyAuthUser:
            chttp.useProxy(proxyAuthUser, proxyAuthPassword)
        if basicAuthUser:
            chttp.useAuth(basicAuthUser, basicAuthPass)
        return chttp.request(follow=onRedirect)

    def onSuccess(self, results, config):
        data = self.new_data()
        perfData = {}
        perfData['time'] = results['time']
        perfData['size'] = results['size']
        ds0 = config.datasources[0]

        message = ("HTTP OK: HTTP/1.1 200 OK"
                   "- {0} bytes in {1:.3f} second response time "
                   "|time={1:.3f}s;;;0.000000 size={0}B;;;0").format(results['size'], results['time'])

        log.debug('{} {}'.format(config.id, message))

        for dp in ds0.points:
            if dp.id in perfData:
                data['values'][None][dp.id] = perfData[dp.id]

        eventKey = ds0.eventKey or 'HttpMonitor'

        data['events'].append({
            'eventKey': eventKey,
            'summary': message,
            'message': message,
            'device': config.id,
            'eventClass': ds0.eventClass,
            'severity': ZenEventClasses.Clear
        })

        return data

    def onError(self, result, config):
        data = self.new_data()
        perfData = {}
        ds0 = config.datasources[0]
        message = '{}'.format(result.getErrorMessage())

        log.error('{} {}'.format(config.id, message))

        eventKey = ds0.eventKey or 'HttpMonitor'
        data['events'].append({
            'eventKey': eventKey,
            'summary': message,
            'message': message,
            'device': config.id,
            'severity': ZenEventClasses.Error,
            'eventClass': ds0.eventClass
        })

        return data

