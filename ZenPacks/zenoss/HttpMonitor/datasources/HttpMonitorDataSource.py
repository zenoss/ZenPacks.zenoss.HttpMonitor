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
import yaml

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

        # Settings from datasource
        component = datasource.component
        hostname = datasource.hostname
        ipAddress = datasource.ipAddress
        port = datasource.port
        useSsl = datasource.useSsl
        url = datasource.url
        basicAuthUser = datasource.basicAuthUser
        basicAuthPass = datasource.basicAuthPass
        onRedirect = datasource.onRedirect
        proxyAuthUser = datasource.proxyAuthUser
        proxyAuthPassword = datasource.proxyAuthPassword
        timeout = datasource.timeout
        regex = datasource.regex
        caseSensitive = datasource.caseSensitive
        invert = datasource.invert

        # Check zHttpMonitorDataSourceSettings zProp. If it is 'enabled' - take values from it.
        # Fall back to default if particular setting is missed in this config.
        z_settings_string = getattr(context, 'zHttpMonitorDataSourceSettings', 'enabled: false')

        try:
            z_settings = yaml.safe_load(z_settings_string)
        except Exception:
            z_settings = {}
        if z_settings.get('enabled'):
            component = z_settings.get('component', component)
            hostname = z_settings.get('hostname', hostname)
            ipAddress = z_settings.get('ipAddress', ipAddress)
            port = z_settings.get('port', port)
            useSsl = z_settings.get('useSsl', useSsl)
            url = z_settings.get('url', url)
            basicAuthUser = z_settings.get('basicAuthUser', basicAuthUser)
            basicAuthPass = z_settings.get('basicAuthPass', basicAuthPass)
            onRedirect = z_settings.get('onRedirect', onRedirect)
            proxyAuthUser = z_settings.get('proxyAuthUser', proxyAuthUser)
            proxyAuthPassword = z_settings.get('proxyAuthPassword', proxyAuthPassword)
            timeout = z_settings.get('timeout', timeout)
            regex = z_settings.get('regex', regex)
            caseSensitive = z_settings.get('caseSensitive', caseSensitive)
            invert = z_settings.get('invert', invert)

        params['componentString'] = datasource.talesEval(component, context)
        params['hostname'] = datasource.talesEval(hostname, context)
        params['ipAddress'] = datasource.talesEval(ipAddress, context)
        params['port'] = datasource.talesEval(port, context)
        params['useSsl'] = datasource.talesEval(useSsl, context)
        params['url'] = datasource.talesEval(url, context)
        params['basicAuthUser'] = datasource.talesEval(basicAuthUser, context)
        params['basicAuthPass'] = datasource.talesEval(basicAuthPass, context)
        params['onRedirect'] = datasource.talesEval(onRedirect, context)
        params['proxyAuthUser'] = datasource.talesEval(proxyAuthUser, context)
        params['proxyAuthPassword'] = datasource.talesEval(proxyAuthPassword, context)
        params['eventKey'] = datasource.talesEval(datasource.eventKey, context)
        params['eventClass'] = datasource.talesEval(datasource.eventClass, context)
        params['timeout'] = datasource.talesEval(timeout, context)
        params['regex'] = datasource.talesEval(regex, context)
        params['caseSensitive'] = datasource.talesEval(caseSensitive, context)
        params['invert'] = datasource.talesEval(invert, context)

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
        log.info("HTTPMonitor collecting started for: {}".format(hostname or ipaddress or url))
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
                data['values'][ds0.component][dp.id] = perfData[dp.id]

        eventKey = ds0.eventKey or 'HttpMonitor'

        data['events'].append({
            'eventKey': eventKey,
            'summary': message,
            'message': message,
            'device': config.id,
            'eventClass': ds0.eventClass,
            'severity': ZenEventClasses.Clear,
            'component': ds0.component or ds0.params['componentString']
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
            'severity': ds0.severity,
            'eventClass': ds0.eventClass,
            'component': ds0.component or ds0.params['componentString']
        })

        return data
