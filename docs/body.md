Background
----------
The ZenPacks.zenoss.HttpMonitor ZenPack monitors the response times of HTTP
server connection requests, and determines whether specific content exists on a
Web page.

Support
-------
This ZenPack is part of Zenoss Core. Open Source users receive community support
for this ZenPack via our online forums. Enterprise support for this ZenPack is
provided to Zenoss customers with an active subscription.

Gallery
-------
[defaultConfiguration.png]: images/defaultConfiguration.png "Default Configuration" class=gallery
[ExampleGraph.png]: images/ExampleGraph.png "Example Graph" class=gallery
[ProxyConfiguration.png]: images/ProxyConfiguration.png "Proxy Configuration" class=gallery
[ProxyPort8080.jpg]: images/ProxyPort8080.jpg "Proxy Configuration With Proxy Port 8080" class=gallery
[ProxyPort8080AndSiteport8888.jpg]: images/ProxyPort8080AndSiteport8888.jpg "Proxy Configuration With Proxy Port 8080 and Web Site Port 8888" class=gallery
[proxyWithAuth.png]: images/proxyWithAuth.png "Proxy Configuration With Credentials" class=gallery
[severalDatasources.png]: images/severalDatasources.png "Ability to add several HttpMonitor datasources to single device" class=gallery


[![][defaultConfiguration.png]][defaultConfiguration.png]
[![][ExampleGraph.png]][ExampleGraph.png]
[![][ProxyConfiguration.png]][ProxyConfiguration.png]
[![][ProxyPort8080.jpg]][ProxyPort8080.jpg]
[![][ProxyPort8080AndSiteport8888.jpg]][ProxyPort8080AndSiteport8888.jpg]
[![][proxyWithAuth.png]][proxyWithAuth.png]
[![][severalDatasources.png]][severalDatasources.png]

Features
--------
HttpMonitor features include:

- Monitors HTTP response time
- Monitors HTTP page size
- Monitors HTTP response code
- Monitors HTTP through Proxy server
- Monitors HTTP with Basic access authentication
- Monitors HTTP specific content on the Web page

Enable Monitoring
-----------------
Follow these steps to enable monitoring:

- Select Infrastructure from the navigation bar.
- Click the device name in the device list. The device overview page appears.
- Expand Monitoring Templates, and then select Device from the left panel.
- Select Bind Templates from the Action menu. The Bind Templates dialog appears.
- Add the HttpMonitor template to the list of selected templates, and then click Submit.

The HttpMonitor template is added to the list of monitoring templates. You can now begin collecting Web server metrics from the device.

A couple of HttpMonitor data sources bind to a single device are possible. It can be done by putting them under the current or separate template(s).
To easily differentiate the events from each of these data sources, theirs "component" field can be populated with unique data.

Check for a Specific URL or Specify Security Settings
-----------------------------------------------------
- Select Infrastructure from the navigation bar.
- Click the device name in the device list. The device overview page appears.
- Select the 'Gear' icon on the bottom panel and select the "Override Template Here" option.
- Choose "HttpMonitor (/)" template and select "Submit". This will create a local copy of the default HttpMonitor template for only this device.
- Select the newly created "HttpMonitor (Locally Defined)" template.
- Select the HttpMonitor data source, and then select View and Edit Details from the Action menu. The Edit Data Source dialog appears.
- Change data source options as needed, and then click Save.

HttpMonitor Content Checking Data Source Options
------------------------------------------------
<table border=2 data-table="resource" style="color: rgb(61, 61, 61); line-height: 175%; background: transparent;">
    <thead>
        <tr data-table-header="togglable">
            <td>Option</td>
            <td>Description</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Port</td>
            <td>The port to connect to HTTP server (default <code>80</code>).</td>
        </tr>
        <tr>
            <td>Use SSL</td>
            <td>Use SSL for the connection (default <code>False</code>).</td>
        </tr>
        <tr>
            <td>URL</td>
            <td>Address of the web page (default <code>/</code>).</td>
        </tr>
        <tr>
            <td>Basic Auth User</td>
            <td>If the website requires credentials, specify the username here (default <code>None</code>).</td>
        </tr>
        <tr>
            <td>Basic Auth Password</td>
            <td>Password for the user (default <code>None</code>).</td>
        </tr>
        <tr>
            <td>Redirect Behavior</td>
            <td>If the web site returns an HTTP redirect, should the probe follow the redirect or create an event? (default <code>follow</code>)<br/>
                <u>ok</u> - Do not follow the redirect and return a positive response<br/>
                <u>fail</u> - Do not follow the redirect and return a negative response<br/>
                <u>follow</u> - Follow redirection<br/>
                <u>stickyhost</u> - Use original hostname (or IP address) on redirect<br/>
                <u>stickyhostport</u> - Use original hostname and port on redirect
            </td>
        </tr>
        <tr>
        <td>Event class</td>
        <td>(default /Status/HTTP)</td>
        </tr>
    </tbody>
</table>


Tuning for Site Responsiveness
------------------------------
- Select Infrastructure from the navigation bar.
- Click the device name in the device list. The device overview page appears.
- Select the 'Gear' icon on the bottom panel and select the "Override Template Here" option.
- Choose "HttpMonitor (/)" template and select "Submit". This will create a local copy of the default HttpMonitor template for only this device.
- Select the newly created "HttpMonitor (Locally Defined)" template.
- Select the HttpMonitor data source, and then select View and Edit Details from the Action menu. The Edit Data Source dialog appears.
- Change data source options as needed, and then click Save.

<table border=3 data-table="resource" style="color: rgb(61, 61, 61); line-height: 175%; background: transparent;">
    <thead>
        <tr data-table-header="togglable">
            <td>Option</td>
            <td>Description</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Timeout (seconds)</td>
            <td>Seconds before connection times out (default: 60)</td>
        </tr>
        <tr>
            <td>Cycle Time (seconds)</td>
            <td>Number of seconds between collection cycles (default: 300 or five minutes)</td>
        </tr>
    </tbody>
</table>


Check for Specific Content on the Web Page
------------------------------------------
This procedure allows Zenoss platform to create an event if content at the web page does not match the expected output.

- Select Infrastructure from the navigation bar.
- Click the device name in the device list. The device overview page appears.
- Select the 'Gear' icon on the bottom panel and select the "Override Template Here" option.
- Choose "HttpMonitor (/)" template and select "Submit". This will create a local copy of the default HttpMonitor template for only this device.
- Select the newly created "HttpMonitor (Locally Defined)" template.
- Select the HttpMonitor data source, and then select View and Edit Details from the Action menu. The Edit Data Source dialog appears.
- Change data source options as needed, and then click Save.

**HttpMonitor Content Checking Data Source Options**

<table border=3 data-table="resource" style="color: rgb(61, 61, 61); line-height: 175%; background: transparent;">
    <thead>
        <tr data-table-header="togglable">
            <td>Option</td>
            <td>Description</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Regular Expression</td>
            <td>A Python regular expression to match text in the web page.</td>
        </tr>
        <tr>
            <td>Case Sensitive</td>
            <td>Is the regular expression case-sensitive or not?</td>
        </tr>
        <tr>
            <td>Invert Expression</td>
            <td>If you would like to test to see if the web page does not contain content matched by a regular expression, check this box.</td>
        </tr>
    </tbody>
</table>


Configuration to Monitor HTTP Through a Proxy Server
------------------------------------------
Example configuration of HttpMonitor to check a website through a Proxy Server
when you have a proxy server with an IP address: 192.168.100.10 on port: 8080
and you have a device on /Devices/HTTP with a name google.com

<table border=2 data-table="resource" style="color: rgb(61, 61, 61); line-height: 175%; background: transparent;">
    <thead>
        <tr data-table-header="togglable">
            <td>Option</td>
            <td>Example value</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>HostName</td>
            <td>${dev/id}</td>
        </tr>
        <tr>
            <td>IP Address or Proxy Address</td>
            <td>192.168.100.10</td>
        </tr>
        <tr>
            <td>Port</td>
            <td>8080</td>
        </tr>
        <tr>
            <td>URL</td>
            <td>/</td>
        </tr>
        <tr>
            <td>Proxy User</td>
            <td>(empty for if proxy anonymous)</td>
        </tr>
        <tr>
            <td>Proxy Password</td>
            <td>(empty for if proxy anonymous)</td>
        </tr>
    </tbody>
</table>

Example configuration of HttpMonitor to check a website through a Proxy Server
when you have a proxy server with an IP address: 192.168.100.10 on port: 8080
and you have a device on /Devices/HTTP with a name google.com and HTTP port 8888

<table border=2 data-table="resource" style="color: rgb(61, 61, 61); line-height: 175%; background: transparent;">
    <thead>
        <tr data-table-header="togglable">
            <td>Option</td>
            <td>Example value</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>HostName</td>
            <td>(empty)</td>
        </tr>
        <tr>
            <td>IP Address or Proxy Address</td>
            <td>192.168.100.10</td>
        </tr>
        <tr>
            <td>Port</td>
            <td>8080</td>
        </tr>
        <tr>
            <td>URL</td>
            <td>http://google.com:8888/</td>
        </tr>
        <tr>
            <td>Proxy User</td>
            <td>(empty if proxy anonymous)</td>
        </tr>
        <tr>
            <td>Proxy Password</td>
            <td>(empty if proxy anonymous)</td>
        </tr>
    </tbody>
</table>

Example configuration of HttpMonitor to check a website through a Proxy Server
when you have a proxy server with an IP address: 192.168.100.127 on port: 8080 and Username: proxy
, Password: myproxypassword, and you have a device on /Devices/HTTP with a name example.org and HTTP port 8888

<table border=2 data-table="resource" style="color: rgb(61, 61, 61); line-height: 175%; background: transparent;">
    <thead>
        <tr data-table-header="togglable">
            <td>Option</td>
            <td>Example value</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>HostName</td>
            <td>(empty)</td>
        </tr>
        <tr>
            <td>IP Address or Proxy Address</td>
            <td>192.168.100.127</td>
        </tr>
        <tr>
            <td>Port</td>
            <td>8080</td>
        </tr>
        <tr>
            <td>URL</td>
            <td>http://example.org:8081/</td>
        </tr>
        <tr>
            <td>Proxy User</td>
            <td>proxy35</td>
        </tr>
        <tr>
            <td>Proxy Password</td>
            <td>mypproxpassword</td>
        </tr>
    </tbody>
</table>

Proxy usage logic
-----------------
HttpMonitor uses the address in the `IP Address or Proxy Address` field as a proxy server
 if the IP address for resolve in the field `URL` and `Host Name` and `IP Address or Proxy Address` do not match


Daemons
-------

<table border=3 data-table="resource" style="color: rgb(61, 61, 61); line-height: 175%; background: transparent;">
    <thead>
        <tr data-table-header="togglable">
            <td>Type</td>
            <td>Name</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Performance Collector</td>
            <td>zenpython</td>
        </tr>
    </tbody>
</table>



Changes
-------

3.1.2

- Improve compatibility with new Python libraries
- Tested with Zenoss Cloud, Zenoss 6.6.0, Zenoss 6.7.0

3.1.1

- Make use of value configured in Datasource "Component" field (ZPS-6133)
- Tested with Zenoss Cloud, Zenoss 6.6.0, Zenoss 6.7.0

3.1.0

- Fix infinity redirection in the case with not full URI path in header Location (ZPS-4904)
- Fix issue when HttpMonitor doesn't check response and doesn't handle either (ZPS-4998)
- Fix crashes of PythonCollector in the case with blank IP Address or Proxy Address fields (ZPS-4986)
- Fix collection of datapoints for component-level datasources (ZPS-5550)
- Provides details on Proxy usage with examples (ZPS-4912)
- Tested with 6.3.2 and Zenoss Cloud


3.0.4

- Fix issue with locally defined monitoring templates after upgrade (ZPS-3817)
- Fix handles bad proxy hostnames (ZPS-3819)
- Adds unittests for regular expression and redirect behavior
- Adds **`Case sensitive/Invert Expression/Regular Expression`** properties into DataSource configuration (ZPS-3867)
- Adds **`Redirect Behavior`** options **`ok/fail/follow/sticky/stickyport`** (ZPS-3867)
- Tested with Zenoss Resource Manager 6.2.0, Zenoss Resource Manager 5.3.3


3.0.0

- Removes **`Case sensitive/Invert Expression/Regular Expressions`** zProperties from DataSource configuration
- Changes **`Redirect Behavior`** list to checkbox
- Removes dependency library **`check_http`** from Nagios Plugins
- Adds unittests
