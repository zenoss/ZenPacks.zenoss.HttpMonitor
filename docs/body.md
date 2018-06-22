Background
----------

The HttpMonitor ZenPack monitors the response times of HTTP server connection requests.

### Prerequisites

- Zenoss (4.2 or newer)
- PythonCollector

### Gallery

[defaultConfiguration.png]: images/defaultConfiguration.png "Default Configuration" class=gallery
[ExampleGraph.png]: images/ExampleGraph.png "Example Graph" class=gallery
[ProxyConfiguration.png]: images/ProxyConfiguration.png "Proxy Configuration" class=gallery


[![][defaultConfiguration.png]][defaultConfiguration.png]
[![][ExampleGraph.png]][ExampleGraph.png]
[![][ProxyConfiguration.png]][ProxyConfiguration.png]


Features
--------

HttpMonitor features include:

- Monitors HTTP response time
- Monitors HTTP page size
- Monitors HTTP response code
- Monitors HTTP through Proxy server
- Monitors HTTP with Basic access authentication

Enable Monitoring
-----------------

Follow these steps to enable monitoring:

- Select Infrastructure from the navigation bar.
- Click the device name in the device list. The device overview page appears.
- Expand Monitoring Templates, and then select Device from the left panel.
- Select Bind Templates from the Action menu. The Bind Templates dialog appears.
- Add the HttpMonitor template to the list of selected templates, and then click Submit. Note: Prior to Zenoss 2.4, this template was not available. If your version is prior to Zenoss 2.4 you must create the template, data source and graphs manually. For more information, refer to Zenoss Service Dynamics Resource Management Administration.

The HttpMonitor template is added to the list of monitoring templates. You can now begin collecting Web server metrics from the device.


Check for a Specific URL or Specify Security Settings
-----------------------------------------------------

- Select Infrastructure from the navigation bar.
- Click the device name in the device list. The device overview page appears.
- Expand Monitoring Templates, and then select Device from the left panel.
- Create a local copy of the template.
- Select the newly created local template copy.
- Select the HttpMonitor data source, and then select View and Edit Details from the Action menu. The Edit Data Source dialog appears.
- Change data source options as needed, and then click Save.


Tuning for Site Responsiveness
------------------------------
- Select Infrastructure from the navigation bar.
- Click the device name in the device list. The device overview page appears.
- Expand Monitoring Templates, and then select Device from the left panel.
- Create a local copy of the template.
- Select the newly created local template copy.
- Select the HttpMonitor data source, and then select View and Edit Details from the Action menu. The Edit Data Source dialog appears.
- Change data source options as needed, and then click Save.

Option	                Description
------                  -----------
Timeout (seconds)	    Seconds before connection times out (default: 60)
Cycle Time (seconds)	Number of seconds between collection cycles (default: 300 or five minutes)
--------------------------------------------------------------------------------------------------
Table: *HTTPMonitor Tunables Data Source Options*

HttpMonitor Content Checking Data Source Options
------------------------------------------------
Option	                Description
------                  -----------
Port	                The port to connect to HTTP server (default `80`).
Use SSL                 Use SSL for the connection (default `False`).
URL                     Address of the web page (default `/`).
Basic Auth User         If the website requires credentials, specify the username here (default `None`).
Basic Auth Password     Password for the user (default `None`).
Follow redirect ?	    If the web site returns an HTTP redirect, should the probe follow the redirect or create an event? (default `True`)
-------------------------------------------------------------------------------------------------------------------------------------------
Table: *HTTPMonitor Content Checking Data Source Options*


Changes
-------

3.1.0

- Fix issue with locally defined monitoring templates after upgrade (ZPS-3817)
- Fix handles bad proxy hostnames (ZPS-3819)

3.0.0

- Removes `Case sensitive/Invert Expression/Regular Expressions` zPropperties from DataSource configuration
- Changes `Redirect Behavior` list to checkbox
- Removes dependency library `check_http` from Nagios Plugins
- Adds unittests
