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

import ast
import logging

from Products.ZenEvents import ZenEventClasses
from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource \
    import PythonDataSource, PythonDataSourcePlugin

from ZenPacks.zenoss.HttpMonitor.http import HTTPMonitor

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
    onRedirect = 'follow'
    onRedirectOptions = ('ok', 'fail', 'follow', 'sticky', 'stickyport')
    proxyAuthUser = ''
    proxyAuthPassword = ''
    regex = ''
    caseSensitive = False
    invert = False
    _properties = PythonDataSource._properties + (
        {'id': 'hostname', 'type': 'string', 'mode': 'w'},
        {'id': 'ipAddress', 'type': 'string', 'mode': 'w'},
        {'id': 'port', 'type': 'int', 'mode': 'w'},
        {'id': 'useSsl', 'type': 'boolean', 'mode': 'w'},
        {'id': 'url', 'type': 'string', 'mode': 'w'},
        {'id': 'basicAuthUser', 'type': 'string', 'mode': 'w'},
        {'id': 'basicAuthPass', 'type': 'string', 'mode': 'w'},
        {'id': 'onRedirect', 'type':'string', 'mode':'w'},
        {'id': 'timeout', 'type': 'int', 'mode': 'w'},
        {'id': 'proxyAuthUser', 'type': 'string', 'mode': 'w'},
        {'id': 'proxyAuthPassword', 'type': 'string', 'mode': 'w'},
        {'id': 'regex', 'type': 'string', 'mode': 'w'},
        {'id': 'caseSensitive', 'type': 'boolean', 'mode': 'w'},
        {'id': 'invert', 'type': 'boolean', 'mode': 'w'},
    )

    def addDataPoints(self):
        if not self.datapoints._getOb('time', None):
            self.manage_addRRDDataPoint('time')
        if not self.datapoints._getOb('size', None):
            self.manage_addRRDDataPoint('size')


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

        params['regex'] = datasource.talesEval(
            datasource.regex, context)

        params['caseSensitive'] = datasource.talesEval(
            datasource.caseSensitive, context)

        params['invert'] = datasource.talesEval(
            datasource.invert, context)

        return params

    def collect(self, config):
        ds0 = config.datasources[0]
        hostname = ds0.params['hostname']
        timeout = int(ds0.params['timeout'])
        port = int(ds0.params['port'])
        useSsl = ast.literal_eval(ds0.params['useSsl'])
        url = ds0.params['url']
        ipaddress = ds0.params['ipAddress']
        regex = ds0.params['regex']
        caseSensitive = ds0.params['caseSensitive']
        invert = ds0.params['invert']
        onRedirect = ds0.params['onRedirect']

        onRedirect = str(onRedirect)

        if onRedirect in ('False', ''):
            onRedirect = "fail"
        elif onRedirect == "True":
            onRedirect = "follow"

        basicAuthUser = ds0.params['basicAuthUser']
        basicAuthPass = ds0.params['basicAuthPass']
        proxyAuthUser = ds0.params['proxyAuthUser']
        proxyAuthPassword = ds0.params['proxyAuthPassword']
        log.info("HTTPMonitor collecting started for a host: {}".format(hostname))
        chttp = HTTPMonitor(ipAddr=ipaddress, hostname=hostname, url=url, port=port, timeout=timeout, ssl=useSsl,
                            follow=onRedirect)
        if proxyAuthUser:
            chttp.useProxy(proxyAuthUser, proxyAuthPassword)
        if basicAuthUser:
            chttp.useAuth(basicAuthUser, basicAuthPass)
        if regex:
            chttp.regex(regex, ast.literal_eval(caseSensitive), ast.literal_eval(invert))
        return chttp.connect()

    def onSuccess(self, results, config):
        data = self.new_data()
        perfData = {}
        perfData['time'] = results['time']
        perfData['size'] = results['size']
        ds0 = config.datasources[0]
        if results.get('msg', ""):
            regex = results['msg'].get('msg')+" -"
            state = results['msg'].get('status')
        else:
            state = "OK"
            regex = ""
        message = ("HTTP {0}: HTTP/1.1 {2} {1} "
                   "- {5} {3} bytes in {4:.3f} second response time "
                   "|time={4:.3f}s;;;0.000000 size={3}B;;;0").format(state, results['message'],
                                                                     results['code'], results['size'],
                                                                     results['time'], regex)

        if state != "OK":
            raise Exception(message)

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
