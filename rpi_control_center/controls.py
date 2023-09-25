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
    last_update = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
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
    def __init__(self, pwm_pin, init_duty=0, freq=50, label='pwm_control' , api_dir='./api/', log_dir='./log/',refresh_rate=1):

        self.label = label
        self.status = False
        self.pwm_pin = pwm_pin
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
        if GPIO.getmode() != GPIO.BCM:
            GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(self.pwm_pin, GPIO.OUT)

        self.pwm = GPIO.PWM(self.pwm_pin, self.freq)
        
        print(f"{self.label} setup completed, sensor initialized")

    def change_frequency(self,freq):

        self.freq=freq 

        self.pwm.ChangeFrequency(self.freq)

        return self.freq

    def change_duty_cycle(self,duty):
        self.duty = duty

        self.pwm.ChangeDutyCycle(self.duty)

        return self.duty
    
    def get_control_readings(self):

        self.control_readings = {'PWM Frequency':self.freq,
                                 'PWM Duty Cycle':self.duty,
                                 'status': 'active' if self.status else 'offline',
                                 'timestamp': datetime.datetime.now().strftime(timestamp_strformat)
                                 }

        return self.control_readings 

    
    @set_thread
    @threaded
    def start(self):

        self.status = True
        self.begin()
        self.pwm.start(self.duty)
        # super().start(self.duty)

        print(f'Starting {self.label} process')
        data = {'label': self.label}

        while self.status:
            data['control_data'] = self.get_control_readings()
            
            push_to_api(self.api_file, data)
            time.sleep(self.refresh_rate)
        
        print(f'Stopping {self.label} thread processes in progress')
        self.change_duty_cycle(0)
        data['control_data'] = self.get_control_readings()
        push_to_api(self.api_file, data)
        self.pwm.stop()
        GPIO.cleanup(self.pwm_pin)
        self.pwm = None
        print('Thread process ended')


    def stop(self):
        self.status = False
        print(f'attempting to stop thread of {self.label}')
