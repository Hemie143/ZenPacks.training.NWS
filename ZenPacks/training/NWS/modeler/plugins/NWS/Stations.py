"""Models locations using the National Weather Service API."""

# stdlib Imports
import json
import urllib

# Twisted Imports
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredList
from twisted.web.client import Agent, readBody
from twisted.internet import reactor
from twisted.web.http_headers import Headers

# Zenoss Imports
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin


class Stations(PythonPlugin):

    """NWS Stations modeler plugin."""
    """Use twisted.web.client.Agent instead of getPage"""

    relname = 'nwsStations'
    modname = 'ZenPacks.training.NWS.NwsStation'

    requiredProperties = (
        'zNwsStates',
    )

    deviceProperties = PythonPlugin.deviceProperties + requiredProperties

    @inlineCallbacks
    def collect(self, device, log):
        """Asynchronously collect data from device. Return a deferred/"""
        log.info('%s: collecting data', device.id)

        NwsStates = getattr(device, 'zNwsStates', None)
        if not NwsStates:
            log.error('%s: %s not set.', device.id, 'zNwsStates')
            returnValue(None)

        deferreds = []
        responses = []

        # TEST: Limit to one state
        NwsStates = NwsStates[:1]

        agent = Agent(reactor)
        headers = {"User-Agent": ["Mozilla/3.0Gold"],
                   }

        for NwsState in NwsStates:
            if NwsState:
                try:
                    url = 'https://api.weather.gov/stations?state={query}'.format(query=urllib.quote(NwsState))
                    response = yield agent.request('GET', url, Headers(headers))
                    response_body = yield readBody(response)
                    response_body = json.loads(response_body)
                    responses.append(response_body)
                except Exception, e:
                    log.error('%s: %s', device.id, e)
                    returnValue(None)
                for feature in response_body.get('features'):
                    url = 'https://api.weather.gov/stations/{query}'.format(
                        query=urllib.quote(feature['properties']['stationIdentifier']))
                    d = agent.request('GET', url, Headers(headers))
                    d.addCallback(readBody)
                    deferreds.append(d)
        results = yield DeferredList(deferreds, consumeErrors=True)
        returnValue((responses, results))

    def process(self, device, results, log):
        """Process results. Return iterable of datamaps or None."""
        rm = self.relMap()

        (generalResults, detailedRawResults) = results

        # TEST: Limit the number of created instances
        count = 0

        detailedResults = {}
        for result in detailedRawResults:
            result = json.loads(result[1])
            id = self.prepId(result['properties']['stationIdentifier'])
            detailedResults[id] = result['properties']
        for result in generalResults:
            for stationResult in result.get('features'):
                if count >= 3:
                    continue
                id = self.prepId(stationResult['properties']['stationIdentifier'])
                zoneLink = detailedResults.get(id, {}).get('forecast', '')
                countyLink = detailedResults.get(id, {}).get('county', '')

                rm.append(self.objectMap({
                    'id': id,
                    'station_id': id,
                    'title': stationResult['properties']['name'],
                    'longitude': stationResult['geometry']['coordinates'][0],
                    'latitude': stationResult['geometry']['coordinates'][1],
                    'timezone': stationResult['properties']['timeZone'],
                    'county': countyLink.split('/')[-1],
                    'nws_zone': zoneLink.split('/')[-1],
                }))
                count += 1

        return rm
