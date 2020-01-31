ZenPack from:
https://help.zenoss.com/dev/zenpack-sdk/tutorials/monitoring-an-http-api


This tutorial will describe an efficient approach to monitoring data via a HTTP API. We’ll start by using zenpack.yaml to extend the Zenoss object model. Then we’ll use a Python modeler plugin to fill out the object model. Then we’ll use PythonCollector to monitor for events, datapoints and even to update the model.

The ZenPack has been edited in order to get rid of the getPage function that is deprecated, as listed here:
https://tahoe-lafs.org/trac/tahoe-lafs/ticket/2857

getPage :
  - doesn't show the HTTP code
  - is restricted to HTTP 1.0 only (no support for HTTP 1.1 or higher)
 
The ZenPack shows the usage of DefferedList, deffereds and callbacks.

TODO: 
  - Refactor the datasource to split process() from collect().


Zenoss
ZenPacks
Training
HTTP API