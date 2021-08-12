import os.path
import json
import threading
import time
import datetime
import RPi.GPIO as GPIO

import logging
import logzero
from logzero import logger, setup_logger
format = '%(color)s[%(levelname)1.1s %(asctime)s %(module)s:%(funcName)s %(thread)d]%(end_color)s %(message)s'
formatter = logzero.LogFormatter(fmt=format)

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
        self.api_file = './api/relay'+self.id +'_'+str(self.pin)+'.json'

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

    @property
    def api_file(self):
        '''
        '''
        return self._api_file

    @api_file.setter
    def api_file(self, value):
        '''
        '''

        self._api_file = value

    def update_api_file(self):

        self.api_file = './api/relay'+self.id +'_'+str(self.pin)+ '.json'

    def push_to_api(self, value = None):
        if value:
            self.api_file = value
        else:
            self.update_api_file()

        timestamp = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        data = {"relay_id":self.id, "name":self.name,"pin":self.pin, "status":self.state, "last updated":timestamp}

        with open(self.api_file, "w") as f:
            f.write(json.dumps(data, indent=4))

    @threaded
    def start(self):
        success = False
        while self.state:
            try:
                while self.state and not success:
                    pin = self.pin
                    GPIO.setup(pin, GPIO.OUT)
                    GPIO.output(pin, GPIO.HIGH)
                    print(f'[{self.id}:{self.name}]GPIO {pin} sucessfull initialized')

                    success = True
            except:
                print(f'[{self.id}:{self.name}]GPIO {pin} failed to initialize')
                exit()
            try:
                while self.state:
                    if GPIO.input(pin):
                        GPIO.output(pin, GPIO.LOW)
                        print(f'[{self.id}:{self.name}]GPIO {pin} Switch ON')

                    else:
                        pass
            except:
                GPIO.output(pin, GPIO.HIGH)
                GPIO.cleanup(pin)

                print(f'[{self.id}:{self.name}]GPIO {pin} Error with the process, switching OFF and cleaning pin')
                exit()


            GPIO.output(pin, GPIO.HIGH)
            GPIO.cleanup(pin)
            print(f'[{self.id}:{self.name}]GPIO {pin} Switch OFF')


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

        relay.push_to_api()

def log_all_relays(dict_of_relays, log_file):

    logger = setup_logger(name=__name__+"status_logger", logfile="./logs/status.log", level=10, formatter = formatter)

    for relay_id, relay in dict_of_relays.items():
        logger.info(f'Relay{relay_id}: Name[{relay.name}], Pin[{relay.pin}], state[{relay.state}]')
