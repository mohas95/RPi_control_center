import os.path
import json
import threading
import time
import RPi.GPIO as GPIO


def threaded(func):
    def wrapper(*args, **kwargs):

        thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()

        return thread
    return wrapper

class Relay():
    def __init__(self, id, name, pin, state=False):
        self.id = id
        self.name = name
        self.pin = pin
        self.state = state
        self.thread = self.start()

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

    @threaded
    def start(self):
        success = False
        while self.state:
            while self.state and not success:
                # try:
                pin = self.pin
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.HIGH)
                print('GPIO sucessfull initialized')

                success = True
                # except:
                #     print('error')
                #     exit()
            while self.state:
                if GPIO.input(pin):
                    print('GPIO hit')
                    GPIO.output(pin, GPIO.LOW)
                else:
                    pass

            GPIO.output(pin, GPIO.HIGH)


########################################## Module functions

def begin():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

def stop():
    GPIO.cleanup()

def load_relay_config(config_json_file):
    '''
    return results: dictionary
    '''
    default_relay_config = {
        "1":{'name':'name1', 'pin':26, 'state':False},
        "2":{'name':'name2', 'pin':20, 'state':False},
        "3":{'name':'name3', 'pin':21, 'state':False},
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

        relay = Relay(id = relay_id,name = relay_properties['name'], pin=relay_properties['pin'], state = relay_properties['state'])

        relay_objects[relay_id] = relay

    return relay_objects


def update_relay_states(dict_of_relays, relay_config_file):
    relay_config= load_relay_config(relay_config_file)

    for relay_id, relay in dict_of_relays.items():

        if relay_config[relay_id]['name'] != relay.name:
            relay.name = relay_config[relay_id]['name']
        else:
            pass

        if relay_config[relay_id]['pin'] != relay.pin:
            relay.pin = relay_config[relay_id]['pin']
        else:
            pass

        if relay_config[relay_id]['state'] != relay.state:
            relay.state = relay_config[relay_id]['state']
        else:
            pass

        if not relay.thread.is_alive():
            relay.thread = relay.start()
        else:
            pass
        # print(relay.thread)

def print_all_relays(dict_of_relays):
    for relay_id, relay in dict_of_relays.items():
        print(f'Relay{relay_id}: Name[{relay.name}], Pin[{relay.pin}], state[{relay.state}]')
