import json
from http import client

from app import database


class StaticFlowPusher:
    """REST client to use the Static Entry Pusher API of the Floodlight
    controller.

    Attributes
    ----------
    self.controller_ip: str
        IP address of the Floodlight controller.
    self.controller_port: str
        Port of the Floodlight controller."""

    def __init__(self):
        self.controller_ip = '127.0.0.1'
        self.controller_port = '8080'

    def rest_call(self, action, uri, data):
        """Executes a REST call to the Floodlight controller.

        Parameters
        ----------
        action: str
            HTTP method.
        uri: str
            URI for the Floodlight controller resources.
        data: dict
            Data to the HTTP request.

        Returns
        -------
        tuple
            Status code and response body returned by server."""

        # HTTP request
        conn = client.HTTPConnection(self.controller_ip, self.controller_port)
        conn.request(action, uri, json.dumps(data),
                     {'Content-type': 'application/json',
                      'Accept': 'application/json'})

        # HTTP response
        resp = conn.getresponse()
        ret = (resp.status, resp.read())
        conn.close()

        return ret

    def get(self):
        """Executes a REST call through GET method.

        Returns
        -------
        dict
            Response body with network data."""

        ret = self.rest_call('GET', '/wm/device/', {})

        return json.loads(ret[1])

    def post(self, data):
        """Executes a REST call through POST method.

        Parameters
        ----------
        data: dict
            Data to the HTTP request.

        Returns
        -------
        bool
            True if the status code is 200 and False otherwise."""

        ret = self.rest_call('POST', '/wm/staticflowpusher/json', data)

        return ret[0] == 200

    def delete(self, data):
        """Executes a REST call through DELETE method.

        Parameters
        ----------
        data: dict
            Data to the HTTP request.

        Returns
        -------
        bool
            True if the status code is 200 and False otherwise."""

        ret = self.rest_call('DELETE', '/wm/staticflowpusher/json', data)

        return ret[0] == 200


class Mitigator(StaticFlowPusher):
    """Mitigates anomalous flows by inserting flow table entries in the
    OpenFlow devices through the Floodlight controller.

    The flow table entries are intended to drop the anomalous packets of an
    attacker device.

    Attributes
    ----------
    self.count: int
        Counter of the flow rules.
    self.blacklist: list
        Anomalous flows to be blocked."""

    def __init__(self, count=0, blacklist):
        super().__init__()
        self.count = count
        self.blacklist = blacklist
        self.rule = {'switch': '', 'name': '', 'cookie': '0',
                     'priority': '32768', 'active': 'true',
                     'hard_timeout': '7200', 'eth_type': '0x0800',
                     'ipv4_src': '', 'ipv4_dst': ''}

    def get_switch(self, entry):
        """Gets the switch where the anomalous device are attached.

        Parameters
        ----------
        entry: str
            Anomalous IP address source.

        Returns
        -------
        str
            Switch identification."""

        network_data = self.get()

        for device in network_data['devices']:
              if device['ipv4']:
                  if entry == device['ipv4'][0]:
                    return device['attachmentPoint'][0]['switch']

    def insert_flows_rules(self):
        """Inserts the flow rules to blocked the anomalous devices.

        Flow rules are saved in a database to allow deletion if the blocked
        device is a false positive."""

        for entry in self.blacklist:
            self.rule['switch'] = self.get_switch(entry[0])
            self.rule['name'] = 'block' + str(self.count)
            self.rule['ipv4_src'] = entry[0]
            self.rule['ipv4_dst'] = entry[1]
            self.post(self.rule)
            self.count += 1

            # saves the flow rules in the database
            database.insert_blacklist(entry + tuple([self.rule['name']]))

    def delete_flow_rule(self, rule_name):
        """Deletes the flow rule in case of a false positive.

        Parameters
        ----------
        rule_name: str
            Rule name to be deleted."""

        self.delete({'name': rule_name})
