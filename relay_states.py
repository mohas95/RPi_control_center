import os.path
import json
import threading

def load_relay_config(config_json_file):
    '''
    return results: dictionary
    '''
    default_relay_config = {
        "1":{'name':'name1', 'pin':26, 'state':None},
        "2":{'name':'name2', 'pin':20, 'state':None},
        "3":{'name':'name3', 'pin':21, 'state':None},
    }

    if os.path.isfile(config_json_file):

        with open(config_json_file, "r") as f:
            result = json.load(f)

    else:
        result = default_relay_config
        with open(config_json_file, "w") as f:
            f.write(json.dumps(result, indent=4))

    return result


def load_relay_objects(relay_config):

    relay_objects = {}

    for relay_id, relay_properties in relay_config.items():

        relay = Relay(id = relay_id,name = relay_properties['name'], pin=relay_properties['pin'])

        relay_objects[relay_id] = relay

    return relay_objects



class Relay():
    def __init__(self, id, name, pin):
        self.id = id
        self.name = name
        self.pin = pin
        self.state = False

    @property
    def id(self):
        '''
        '''
        return self._id

    @id.setter
    def id(self, value):
        '''
        '''
        self._id = value

    @property
    def name(self):
        '''
        '''
        return self._name

    @name.setter
    def name(self, value):
        '''
        '''
        self._name = value

    @property
    def pin(self):
        '''
        '''
        return self._pin

    @pin.setter
    def pin(self, value):
        '''
        '''
        self._pin = value

    @property
    def state(self):
        '''
        '''
        return self._state

    @state.setter
    def state(self, value):
        '''
        '''
        self._state = value
