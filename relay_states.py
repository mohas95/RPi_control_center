import os
import os.path
import json
import threading
import time
import datetime
import RPi.GPIO as GPIO

import logging
import logzero
from logzero import logger, setup_logger

########################################################### Global Variables
# Default configuration for a 3 channel relay, this can be modified for whatever you want the default state to be
default_relay_config = {
        "1":{'name':'name1', 'pin':26, 'state':False},
        "2":{'name':'name2', 'pin':20, 'state':False},
        "3":{'name':'name3', 'pin':21, 'state':False},
}

format = '%(color)s[%(levelname)1.1s %(asctime)s %(module)s:%(funcName)s %(thread)d]%(end_color)s %(message)s' # format for the logzero logger
formatter = logzero.LogFormatter(fmt=format) # format object for logzero logger

########################################################### Wrapper/decorator definition function
def threaded(func):
    '''

    '''
    def wrapper(*args, **kwargs):

        thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=False)
        thread.start()

        return thread
    return wrapper

########################################################### Classes
##################### Relay Class
class Relay():
    """
    A class to represent a relay. Supports non-blocking multi-process threading,
    for near-realtime control of individual relays

    Attributes
    ----------
    id : str
        Relay id
    name : str
        Name of the relay
    pin : int
        Pin attributed to relay
    state : bool
        State of the relay (ON or OFF)
    refresh_rate : int
        Refresh rate of state check
    api_file : str
        location of the api_file
    logger : logging.logger
        logger object
    thread : threading.thread
        thread object for parallel processing

    Methods
    -------
    push_to_api(custom_api_file = None):
        Prints the person's name and age.

    @threaded
    def start():
        Prints the person's name and age.
    """

    def __init__(self, id, name, pin, state=False, refresh_rate = 1, log_file = './logs/process.log'):
        """
        Constructs all the necessary attributes for the Relay object.

        Parameters
        ----------
            id : str
                Relay id
            name : str
                Name of the relay
            pin : int
                Pin attributed to relay
            state : int
                State of the relay (ON or OFF)
            refresh_rate : int
                Refresh rate of state check
            log_file : str
                location of logfile
        """
        self.id = id
        self.name = name
        self.pin = pin
        self.state = state
        self.refresh_rate = refresh_rate
        self.api_file = './api/relay'+self.id +'_'+str(self.pin)+'.json'
        self.logger = setup_logger(name=str(__name__)+"_process_logger", logfile=log_file, level=10, formatter = formatter, maxBytes=2e6, backupCount=3)
        self.thread = self.start()

    @property
    def id(self):
        """Return the id of the relay."""
        return self._id

    @id.setter
    def id(self, value):
        """Set the id string of the relay."""
        self._id = str(value)

    @property
    def name(self):
        """Return the name of the relay."""
        return self._name

    @name.setter
    def name(self, value):
        """Set the name string of the relay."""
        self._name = str(value)

    @property
    def pin(self):
        """Return the pin of the relay."""
        return self._pin

    @pin.setter
    def pin(self, value):
        """Set the pin of the relay."""
        if not isinstance(value, int):
            raise TypeError("Pin must be an integer value")
        self._pin = value

    @property
    def state(self):
        """Return the state of the relay."""
        return self._state

    @state.setter
    def state(self, value):
        """Set the state of the relay."""
        if not isinstance(value, bool):
            raise TypeError("State can only be set to a bool variable")
        self._state = value

    @property
    def refresh_rate(self):
        """Return the refresh rate of the relay."""
        return self._refresh_rate

    @refresh_rate.setter
    def refresh_rate(self, value):
        """Set the refresh rate of the relay."""
        if not isinstance(value, int):
            raise TypeError("refresh rate must be an integer value")
        self._refresh_rate = value

    @property
    def logger(self):
        """Return the logger object file location of the relay."""
        return self._logger

    @logger.setter
    def logger(self, value):
        """Set the logger of the relay."""
        if not instance(value, logging.logger):
            raise TypeError("refresh rate must be an integer value")
        self._logger = value

    @property
    def api_file(self):
        """Return the API file location of the relay."""
        return self._api_file

    @api_file.setter
    def api_file(self, value):
        """Set the API file location of the relay."""
        if not isinstance(value, str):
            raise TypeError("API file must be a string")
        self._api_file = value

    def push_to_api(self, custom_api_file = None):
        """Takes the api file attribute or custum api_file and pushes the state and attributes of the relay to the file"""
        if custom_api_file:
            self.api_file = custom_api_file
        else:
            self.api_file = './api/relay'+self.id +'_'+str(self.pin)+ '.json'
        timestamp = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        data = {"relay_id":self.id, "name":self.name,"pin":self.pin, "status":self.state, "last updated":timestamp}

        with open(self.api_file, "w") as f:
            f.write(json.dumps(data, indent=4))

    @threaded
    def start(self):
        """Starts the non-blocking parallel relay thread controlling physical state of the relay based on its attributes"""
        success = False
        while self.state:
            try:
                while self.state and not success:
                    pin = self.pin
                    GPIO.setup(pin, GPIO.OUT)
                    GPIO.output(pin, GPIO.HIGH)
                    self.logger.info(f'[{self.id}:{self.name}]GPIO {pin} sucessfull initialized')
                    success = True
            except:
                self.logger.error(f'[{self.id}:{self.name}]GPIO {pin} failed to initialize')
                exit()
            try:
                while self.state:
                    if GPIO.input(pin):
                        GPIO.output(pin, GPIO.LOW)
                        self.logger.info(f'[{self.id}:{self.name}]GPIO {pin} Switch ON')
                    else:
                        pass
                    time.sleep(self.refresh_rate)
            except:
                GPIO.output(pin, GPIO.HIGH)
                GPIO.cleanup(pin)
                self.logger.error(f'[{self.id}:{self.name}]GPIO {pin} Error with the process, switching OFF and cleaning pin')
                exit()
            GPIO.output(pin, GPIO.HIGH)
            GPIO.cleanup(pin)
            self.logger.info(f'[{self.id}:{self.name}]GPIO {pin} Switch OFF')

##################### BulkUpdater Class
class BulkUpdater():
    def __init__(self,config_file, default_config = default_relay_config , refresh_rate = 1, log_file = './logs/system.log'):
        self.status = False
        self.default_config = default_config
        self.config_file = config_file
        self.saved_config = None
        self.refresh_rate = refresh_rate
        self.relay_dict = self.load_relay_objects()
        self.logger = setup_logger(name=str(__name__)+"_status_logger", logfile=log_file, level=10, formatter = formatter, maxBytes=2e6, backupCount=3)

    @property
    def status(self):
        '''
        '''
        return self._status

    @status.setter
    def status(self, value):
        '''
        '''
        self._status = value

    @property
    def default_config(self):
        '''
        '''
        return self._default_config

    @default_config.setter
    def default_config(self, value):
        '''
        '''
        self._default_config = value
    @property
    def config_file(self):
        '''
        '''
        return self._config_file

    @config_file.setter
    def config_file(self, value):
        '''
        '''
        self._config_file = value


    @property
    def saved_config(self):
        '''
        '''
        return self._saved_config

    @saved_config.setter
    def saved_config(self, value):
        '''
        '''
        self._saved_config = value

    @property
    def relay_dict(self):
        '''
        '''
        return self._relay_dict

    @relay_dict.setter
    def relay_dict(self, value):
        '''
        '''
        self._relay_dict = value

    @property
    def refresh_rate(self):
        '''
        '''
        return self._refresh_rate

    @refresh_rate.setter
    def refresh_rate(self, value):
        '''
        '''
        self._refresh_rate = value

    @property
    def logger(self):
        '''
        '''
        return self._logger

    @logger.setter
    def logger(self, value):
        '''
        '''
        self._logger = value

    def load_config(self):
        '''
        return results: dictionary
        '''
        try:
            if os.path.isfile(self.config_file):
                try:
                    with open(self.config_file, "r") as f:
                        result = json.load(f)
                except:
                    if self.saved_config:
                        result = self.saved_config
                        with open(self.config_file, "w") as f:
                            f.write(json.dumps(result, indent=4))
                        print(f'Error, currupt relay config file, loading the last saved configuration: {self.config_file}')
                    else:
                        result = self.default_config
                        with open(self.config_file, "w") as f:
                            f.write(json.dumps(result, indent=4))
                        print(f'Error, currupt relay config file, could not get last known state creating a default file with default parameters: {self.config_file}')
            else:
                result = self.default_config
                with open(self.config_file, "w") as f:
                    f.write(json.dumps(result, indent=4))
                print(f'Relay config file not found, creating a default file with default parameters: {self.config_file}')

            self.saved_config = result
            return result

        except:
            print(f'Major Error, config file could not be loaded')
            exit()


    def load_relay_objects(self):
        '''
        '''
        try:
            self.load_config()

            relay_objects = {}

            for relay_id, relay_properties in self.saved_config.items():

                relay = Relay(id = relay_id,name = relay_properties['name'], pin=relay_properties['pin'], state = relay_properties['state'], refresh_rate = self.refresh_rate)

                relay_objects[relay_id] = relay

            self.relay_dict = relay_objects

            print('Relay objects instantiated and loaded')

            return relay_objects

        except:
            print('Major Error relay objects could not be loaded')
            exit()

    def update_relay_states(self):
        '''
        '''
        try:
            self.load_config()

            for relay_id, relay in self.relay_dict.items():

                if self.saved_config[relay_id]['name'] != relay.name:
                    relay.name = self.saved_config[relay_id]['name']
                else:
                    pass

                if self.saved_config[relay_id]['pin'] != relay.pin:
                    relay.pin = self.saved_config[relay_id]['pin']
                else:
                    pass

                if self.saved_config[relay_id]['state'] != relay.state:
                    relay.state = self.saved_config[relay_id]['state']
                else:
                    pass

                if not relay.thread.is_alive():
                    relay.thread = relay.start()
                else:
                    pass

                relay.push_to_api()

                self.logger.info(f'Relay{relay_id}: Name[{relay.name}], Pin[{relay.pin}], state[{relay.state}]')

        except:
            self.logger.info('Major Error in updating')
            exit()

    def update_config_file(self, relay_id, state = False):
        '''
        '''
        try:
            self.load_config()

            self.saved_config[relay_id]['state'] = state

            with open(self.config_file, "w") as f:
                f.write(json.dumps(self.saved_config, indent=4))

            state_string = ' OFF' if state==False else ' ON' if state ==True else ' ?'
            print(f'Successful changed relay {relay_id} {state_string} in config file: {self.config_file}')
        except:
            print(f'Major Error could not relay {relay_id} {state_string} in config file: {self.config_file}')
            exit()

    def safe_stop_all_relays(self):
        '''
        '''
        self.status = False

        for relay_id, relay in self.relay_dict.items():
            self.update_config_file(relay_id = relay_id, state = False)

        self.update_relay_states()

        time.sleep(10)

        print('Safely stopped all relays')

    def force_quit(self):
        '''
        '''
        print('Force Quit!')
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        else:
            print("The file does not exist")

        self.load_config()
        GPIO.cleanup()
        exit()

    @threaded
    def start(self):
        '''
        '''

        self.status = True
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        try:
            while self.status:
                self.update_relay_states()
                time.sleep(self.refresh_rate)

            self.safe_stop_all_relays()

        except:
            try:
                self.safe_stop_all_relays()
            except:
                self.force_quit()
            print('Error, Stopping the relay processes')
            exit()

    def stop(self):
        '''
        '''
        self.status = False

########################################################### Main Function
if __name__ == '__main__':
    control_box = BulkUpdater(config_file = './relay_config.json', default_config = default_relay_config , refresh_rate = 1)
    control_box.start()


    ######### You can put any code because this function is non-blocking
    try:
        while True:
            time.sleep(5)
    except:
        control_box.stop()
