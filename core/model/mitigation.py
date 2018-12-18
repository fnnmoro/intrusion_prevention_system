from http import client
import json
import database


class StaticFlowPusher:

    def __init__(self):
        self.server = '127.0.0.1'
        self.path = '/wm/device/'
        self.headers = {'Content-type': 'application/json',
                       'Accept': 'application/json'}

    def get(self):
        ret = self.rest_call({}, 'GET')

        return json.loads(ret[2])

    def set(self, data):
        ret = self.rest_call(data, 'POST')

        return ret[0] == 200

    def delete(self, data):
        ret = self.rest_call(data, 'DELETE')

        return ret[0] == 200

    def rest_call(self, data, action):
        body = json.dumps(data)

        conn = client.HTTPConnection(self.server, 8080)
        conn.request(action, self.path, body, self.headers)
        resp = conn.getresponse()

        ret = (resp.status, resp.reason, resp.read())
        conn.close()

        return ret


class Mitigator:

    def __init__(self, blacklist=None):
        self.count = 0
        self.blacklist = blacklist
        self.pusher = StaticFlowPusher()
        self.rule = {'switch': '', 'name': '', 'cookie': '0',
                     'priority': '32768', 'active': 'true',
                     'hard_timeout': '7200', 'eth_type': '0x0800',
                     'ipv4_src': '', 'ipv4_dst': ''}

    def get_switch(self, entry):
        self.pusher.path = '/wm/device/'
        data = self.pusher.get()

        for device in data['devices']:
              if device['ipv4']:
                  if entry == device['ipv4'][0]:
                    return device['attachmentPoint'][0]['switch']

    def insert_rule(self):
        for entry in self.blacklist:
            self.rule['switch'] = self.get_switch(entry[0])
            self.rule['name'] = 'block' + str(self.count)
            self.rule['ipv4_src'] = entry[0]
            self.rule['ipv4_dst'] = entry[1]

            self.pusher.path = '/wm/staticflowpusher/json'
            self.pusher.set(self.rule)
            self.count += 1

            database.store_blacklist(entry + tuple([self.rule['name']]))

    def delete_rule(self, rule_name):
        self.pusher.path = '/wm/staticflowpusher/json'
        self.pusher.delete({'name': rule_name})
