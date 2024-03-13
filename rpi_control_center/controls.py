import os
import os.path
import json
import threading
import time
import datetime
import RPi.GPIO as GPIO
import pigpio

import logging
import logzero
from logzero import logger, setup_logger

########################################################### Global Variables
format = '%(color)s[%(levelname)1.1s %(asctime)s %(name)s :%(funcName)s %(thread)d]%(end_color)s %(message)s' # format for the logzero logger
formatter = logzero.LogFormatter(fmt=format) # format object for logzero logger
debug_mode = False #debug mode for developers
timestamp_strformat = '%Y/%m/%d %H:%M:%S'


########################################################### Wrapper/decorator & Helper functions
def threaded(func):
    """start and return a thread of the passed in function. Threadify a function with the @threaded decorator"""
    def wrapper(*args,**kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=False)
        thread.start()
        return thread
    return wrapper

def push_to_api(api_file,data):
    """Push data in json format to an api file"""
    last_update = datetime.datetime.now().strftime(timestamp_strformat)
    data["last updated"] = last_update
    with open(api_file,"w") as f:
        f.write(json.dumps(data,indent=4))

def delete_file(file):
    """delete file"""
    if os.path.exists(file):
        os.remove(file)
        print(f'{file} removed')
    else:
        print(f'{file} Does not exist')
        pass

def initiate_file(dir, filename):
    """This function checks whether a directory exists and if not creates it"""
    try:
        if not os.path.exists(dir):
            os.makedirs(dir)
        file_location = dir+filename

        return file_location

    except:
        print('could not create file path, exiting')
        sys.exit()

######################################################################## Classes

class pwm_control():
    '''
    please note that duty cycle is out of 255 for pigio
    '''
    def __init__(self, pwm_pin, init_duty=0, freq=50, label='pwm_control', driver= 'RPi.GPIO' , api_dir='./api/', log_dir='./log/',refresh_rate=1):

        self.label = label
        self.status = False
        self.pwm_pin = pwm_pin
        self.driver= driver
        self.pwm=None
        self.freq=freq
        self.duty=init_duty
        self.api_file = initiate_file(api_dir,label+".json")
        self.log_file = initiate_file(log_dir,label+"-process.log")
        self.refresh_rate = refresh_rate
        self.logger = None
        self.thread = None
        self.control_readings = self.get_control_readings()



    def set_thread(func):
        """Decorator Function in order to set the thread property of the object to the output of a function returning  a thread object"""
        def wrapper(self):
            self.thread = func(self)
            print(f'thread object for {self.label} set as {self.thread}')
            return self.thread
        return wrapper

    def begin(self):
        """
        initialize and setup the sensor
        """ 
        if self.driver == 'RPi.GPIO':
            if GPIO.getmode() != GPIO.BCM:
                GPIO.setmode(GPIO.BCM)
            
            GPIO.setup(self.pwm_pin, GPIO.OUT)

            self.pwm = GPIO.PWM(self.pwm_pin, self.freq)
            self.pwm.start(self.duty)
        
        elif self.driver == 'pigpio':
            self.pwm = pigpio.pi()
            self.pwm.set_PWM_frequency(self.pwm_pin, self.freq)
            self.pwm.set_PWM_dutycycle(self.pwm_pin, self.duty)
        
        print(f"{self.label} setup completed, pwm initialized using {self.driver}")

    def change_frequency(self,freq):

        self.freq=freq 

        if self.driver=='RPi.GPIO':
            self.pwm.ChangeFrequency(self.freq)
        elif self.driver == 'pigpio':
            self.pwm.set_PWM_frequency(self.pwm_pin, self.freq)

        return self.freq

    def change_duty_cycle(self,duty):
        self.duty = duty


        if self.driver=='RPi.GPIO':
            self.pwm.ChangeDutyCycle(self.duty)

        elif self.driver == 'pigpio':
            self.pwm.set_PWM_dutycycle(self.pwm_pin, self.duty)

        return self.duty
    
    def get_control_readings(self):


        self.control_readings = {'PWM Frequency Hz':self.freq,
                                 'PWM Duty Cycle %': round((self.duty/255)*100,2) if self.driver =='pigpio' else self.duty,
                                 'PWM Driver':self.driver,
                                 'status': 'active' if self.status else 'offline',
                                 'timestamp': datetime.datetime.now().strftime(timestamp_strformat)
                                 }

        return self.control_readings 

    
    @set_thread
    @threaded
    def start(self):

        self.status = True
        self.begin()            

        print(f'Starting {self.label} process')
        data = {'label': self.label}

        while self.status:
            data['status'] = self.status
            data['control_data'] = self.get_control_readings()
            
            push_to_api(self.api_file, data)
            time.sleep(self.refresh_rate)
        
        print(f'Stopping {self.label} thread processes in progress')
        
        self.change_duty_cycle(0)
        
        data['status'] = self.status 
        data['control_data'] = self.get_control_readings()
        push_to_api(self.api_file, data)
        self.pwm.stop()
        if self.driver =='RPi.GPIO': GPIO.cleanup(self.pwm_pin)
        self.pwm = None
        print('Thread process ended')


    def stop(self):
        self.status = False
        print(f'attempting to stop thread of {self.label}')


default_relay_config = {
        "relay1":{'pin':26, 'state':False, 'config':'no'},
        "relay2":{'pin':20, 'state':False, 'config':'no'},
        "relay3":{'pin':21, 'state':False, 'config':'no'},
}

class relay_engine():
    
    def __init__(self, relay_config = default_relay_config, label='relays', api_dir='./api/', log_dir='./log/',refresh_rate=1):

        self.label = label
        self.status = False
        self.relay_config = relay_config
        self.api_file = initiate_file(api_dir,label+".json")
        self.log_file = initiate_file(log_dir,label+"-process.log")
        self.refresh_rate = refresh_rate
        self.logger = None
        self.thread = None
        self.control_readings = self.get_control_readings()

    def set_thread(func):
        """Decorator Function in order to set the thread property of the object to the output of a function returning  a thread object"""
        def wrapper(self):
            self.thread = func(self)
            print(f'thread object for {self.label} set as {self.thread}')
            return self.thread
        return wrapper

    def get_on_state(self,relay):

        if self.relay_config[relay]['config'] == 'no':
            on_state = GPIO.LOW
        elif self.relay_config[relay]['config'] ==  'nc':
            on_state =GPIO.HIGH
        else:
            raise ValueError("proper relay config not provided, no or nc only")

        return on_state

    def get_off_state(self,relay):

        if self.relay_config[relay]['config'] == 'no':
            off_state = GPIO.HIGH
        elif self.relay_config[relay]['config'] ==  'nc':
            off_state =GPIO.LOW
        else:
            raise ValueError("proper relay config not provided, no or nc only")

        return off_state      

    def get_control_readings(self):
        
        return self.relay_config

    def set_relay_state(self, relay, state):
        '''Sets the relay state given the relay name and the state
            True means on_state, False means off_state
        
        '''
        if self.relay_config[relay]['state'] != state:
            self.relay_config[relay]['state'] = state
            self.relay_config[relay]['last_changed'] = datetime.datetime.now().strftime(timestamp_strformat)
        
        if 'last_changed' not in self.relay_config[relay] or not self.relay_config[relay]['last_changed']:
            self.relay_config[relay]['last_changed'] = datetime.datetime.now().strftime(timestamp_strformat)

        GPIO.output(self.relay_config[relay]['pin'], self.get_on_state(relay) if self.relay_config[relay]['state'] else self.get_off_state(relay))


    def begin(self):
        if GPIO.getmode() != GPIO.BCM:
            GPIO.setmode(GPIO.BCM)
        
        for relay, relay_params in self.relay_config.items():
            GPIO.setup(relay_params['pin'], GPIO.OUT)
            self.set_relay_state(relay, relay_params['state'])

            print(f"{relay} setup completed, relay initialized {'high' if relay_params['state']==True else 'low'} at pin {relay_params['pin']}")
        
        time.sleep(5)

        print(f"{self.label} setup completed, relays initialized")

    @set_thread
    @threaded
    def start(self):
        
        self.status = True
        self.begin()            

        print(f'Starting {self.label} process')
        data = {'label': self.label}

        while self.status:
            data['status'] = self.status 
            data['control_data'] = self.get_control_readings()
            
            push_to_api(self.api_file, data)
            time.sleep(self.refresh_rate)
        
        print(f'Stopping {self.label} thread processes in progress')
        
        for relay, relay_params in self.relay_config.items():
            self.set_relay_state(relay, False)
            GPIO.cleanup(relay_params['pin'])

            print(f"{relay} stopped, relay state set to {'high' if self.relay_config[relay]['state']==True else 'low'} at pin {self.relay_config[relay]['pin']}")

        data['status'] = self.status 
        data['control_data'] = self.get_control_readings()
        push_to_api(self.api_file, data)
        
        print('Thread process ended')


    def stop(self):
        self.status = False
        print(f'attempting to stop thread of {self.label}')



if __name__ == '__main__':

    relay_config = {
        "relay1":{'pin':26, 'state':False, 'config':'no'},
        "relay2":{'pin':20, 'state':False, 'config':'no'},
        "relay3":{'pin':21, 'state':False, 'config':'no'},
    }

    relay_group1 = relay_engine(relay_config=relay_config, label='test_relays', api_dir='./api/', log_dir='./log/',refresh_rate=1)

    relay_group1.start()

    try:
        while True:
            time.sleep(5)
            relay_group1.set_relay_state('relay1',True)
            time.sleep(5)
            relay_group1.set_relay_state('relay2',True)
            time.sleep(5)
            relay_group1.set_relay_state('relay3',True)
            time.sleep(5)
            relay_group1.set_relay_state('relay1',False)
            time.sleep(5)
            relay_group1.set_relay_state('relay2',False)
            time.sleep(5)
            relay_group1.set_relay_state('relay3',False)
    except:
        relay_group1.stop()
