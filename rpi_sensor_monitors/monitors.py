import json
import threading
import datetime
import time
import os
import os.path
import sys
from .gravity import DFRobot_BME680, DFRobot_BME280
import RPi.GPIO as GPIO

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

class BME680():
	"""
	A class to represents an Interface for reading Atlas Scientific Sensors
	connected to rpi via i2c bus(uses AtlasI2C Class provided by Atlas Scientific).
	This class supports non-blocking multi-process threading, for near-realtime
	monitoring of reading of Atlas Scientific sensors connected on the I2Cbus
	----------
	label : str
		label given to the class of Atlas Scientific Sensors, name used for filing
	status : bool
		The status of the object, active or inactive
	devices : list(DFRobot_BME680 obj)
		the list of Atlas sensor objects initiated from the begin() function
	sensor_readings : dict()
		dictionary of the latest readings of all sensors with respoective properties
	api_file : str
		location of the api_file
	log_file : str
		location of the log_file
	refresh_rate : int
		Refresh rate of state check
	logger : logging.logger
		logger object
	thread : threading.thread
		thread object associated with the parallel process, when starting start() function is called

	Methods
	-------
	set_thread(func):
		Decorator Function in order to set the thread property of the object to
		the output of a function returning  a thread object
	begin():
		Initiates the device objects representing all Atlas Scientific Sensors
		connected to the i2c bus. it also initiates the refreshrate.
		call this before starting any process!
	print_devices():
		prints all Atlas devices connected to the i2c bus
	get_sensor_readings():
		retrieves all sensor readings from the list of devices
	@set_thread
	@threaded
	start():
		Return a thread and start the non-blocking parallel thread which is a driver for
		getting the sensor readings and pushing to an api
	stop():
		set status to False, which in turn will end the while loop of the active thread
	"""

	def __init__(self, label='BME680' , api_dir='./api/', log_dir='./log/',refresh_rate=1):
		self._label = label
		self._status = False
		self.sensor = None
		self._sensor_readings = None
		self._api_file = initiate_file(api_dir,label+".json")
		self._log_file = initiate_file(log_dir,label+"-process.log")
		self._refresh_rate = refresh_rate
		self._logger = None
		self._thread = None

	@property
	def label(self):
		"""return the label of the object"""
		return self._label

	@label.setter
	def label(self, value):
		"""set the label of the object"""
		self._label = value

	@property
	def status(self):
		"""return the status of the object"""
		return self._status

	@status.setter
	def status(self, value):
		"""set the status of the object"""
		self._status = value

	@property
	def sensor_readings(self):
		"""return the sensor_readings of the object"""
		return self._sensor_readings

	@sensor_readings.setter
	def sensor_readings(self, value):
		"""set the sensor_readings of the object"""
		self._sensor_readings = value

	@property
	def api_file(self):
		"""return the api_file of the object"""
		return self._api_file

	@api_file.setter
	def api_file(self, value):
		"""set the api_file of the object"""
		self._api_file = value

	@property
	def log_file(self):
		"""return the log_file of the object"""
		return self._log_file

	@log_file.setter
	def log_file(self, value):
		"""set the log_file of the object"""
		self._log_file = value

	@property
	def refresh_rate(self):
		"""return the refresh_rate of the object"""
		return self._refresh_rate

	@refresh_rate.setter
	def refresh_rate(self, value):
		"""set the refresh_rate of the object"""
		self._refresh_rate = value

	@property
	def logger(self):
		"""return the logger of the object"""
		return self._logger

	@logger.setter
	def logger(self, value):
		"""set the logger of the object"""
		self._logger = value

	@property
	def thread(self):
		"""return the thread of the object"""
		return self._thread

	@thread.setter
	def thread(self, value):
		"""set the thread of the object"""
		self._thread = value

	def set_thread(func):
		"""Decorator Function in order to set the thread property of the object to the output of a function returning  a thread object"""
		def wrapper(self):
			self.thread = func(self)
			print(f'thread object for {self.label} set as {self.thread}')
			return self.thread
		return wrapper

	def begin(self):
		""""""
		sensor = DFRobot_BME680.DFRobot_BME680()
		sensor.set_humidity_oversample(sensor.OS_2X) #Oversampling value: OS_NONE, OS_1X, OS_2X, OS_4X, OS_8X, OS_16X
		sensor.set_pressure_oversample(sensor.OS_4X) #Oversampling value: OS_NONE, OS_1X, OS_2X, OS_4X, OS_8X, OS_16X
		sensor.set_temperature_oversample(sensor.OS_8X) #Oversampling value: OS_NONE, OS_1X, OS_2X, OS_4X, OS_8X, OS_16X
		sensor.set_filter(sensor.FILTER_SIZE_3) #increasing resolution but reducing bandwidth

		sensor.set_gas_status(sensor.ENABLE_GAS_MEAS) #1 for enable and 0 for disable
		sensor.set_gas_heater_temperature(320) #value:target temperature in degrees celsius, between 200 ~ 400
		sensor.set_gas_heater_duration(150) #value:target duration in milliseconds, between 1 and 4032
		sensor.select_gas_heater_profile(0) #value:current gas sensor conversion profile: 0 to 9

		self.sensor = sensor

	def get_sensor_readings(self):

		if self.sensor.get_sensor_data():
			sensor_data = { 'Temperature,C':self.sensor.data.temperature,
							'Humidity,%RH': self.sensor.data.humidity,
							'Pressure,hPa': self.sensor.data.pressure,
							'timestamp': datetime.datetime.now().strftime(timestamp_strformat)
							}

			self.sensor_readings = sensor_data
		else:
			self.sensor_readings = None

		return self.sensor_readings

	@set_thread
	@threaded
	def start(self):
		self.status = True
		print(f'Starting {self.label} process')
		data = {'label':self.label}
		self.begin()

		while self.status:
			data['sensor_data'] = self.get_sensor_readings()
			push_to_api(self.api_file, data)
			time.sleep(self.refresh_rate)

		print(f'Stopping {self.label} thread processes in progress')
		print('Thread process ended')

	def stop(self):
		self.status = False
		print(f'attempting to stop thread of {self.label}')


class ultrasonic():
	def __init__(self, trig_out_pin, echo_in_pin, timeout=5, label='HC-SR04P' , api_dir='./api/', log_dir='./log/',refresh_rate=1):
		self.label = label
		self.status = False
		self.trig_out_pin = trig_out_pin
		self.echo_in_pin = echo_in_pin
		self.timeout = timeout
		self.sensor_readings = None
		self.api_file = initiate_file(api_dir,label+".json")
		self.log_file = initiate_file(log_dir,label+"-process.log")
		self.refresh_rate = refresh_rate
		self.logger = None
		self.thread = None

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
		
		GPIO.setup(self.trig_out_pin, GPIO.OUT)
		GPIO.setup(self.echo_in_pin, GPIO.IN)
		GPIO.output(self.trig_out_pin, GPIO.LOW)
		time.sleep(5)

		print(f"{self.label} setup completed, sensor initialized")

	def get_distance(self):
		
		GPIO.output(self.trig_out_pin, GPIO.HIGH)
		time.sleep(0.00001)
		GPIO.output(self.trig_out_pin, GPIO.LOW)

		time_start = time.time()

		while GPIO.input(self.echo_in_pin) == GPIO.LOW:
			if time.time()-time_start > self.timeout:
				raise TimeoutError("timeout while waiting for signal to go high")


		while GPIO.input(self.echo_in_pin) == GPIO.HIGH:
			if time.time()-time_start > self.timeout:
				raise TimeoutError("timeout while waiting for signal to go low")

		time_stop = time.time()

		pulse_duration = time_stop - time_start
		
		distance = pulse_duration * 34300/2

		distance = round(distance,2)

		return distance, pulse_duration

		
	def get_sensor_readings(self,num_itr=1):

		cum_dist = 0
		cum_pulse = 0

		for i in range(num_itr):

			try:
				dist, pulse_duration = self.get_distance()
			except:
				return None
			
			cum_dist += dist
			cum_pulse +=pulse_duration

		avg_dist = cum_dist / num_itr
		avg_pulse = cum_pulse / num_itr

		sensor_reading = {  'distance,cm':avg_dist,
		    				'pulse duration,s':avg_pulse,
							'samples taken':num_itr,
							'timestamp': datetime.datetime.now().strftime(timestamp_strformat)
							}

		return sensor_reading

	
	@set_thread
	@threaded
	def start(self):
		self.status = True
		print(f'Starting {self.label} process')
		data = {'label':self.label}
		self.begin()

		while self.status:
			data['sensor_data'] = self.get_sensor_readings()
			push_to_api(self.api_file, data)
			time.sleep(self.refresh_rate)

		print(f'Stopping {self.label} thread processes in progress')
		print('Thread process ended')

	def stop(self):
		self.status = False
		print(f'attempting to stop thread of {self.label}')


if __name__ == '__main__':

	water_level = ultrasonic(26,19)
	water_level.start()
	time.sleep(60)
	water_level.stop()
	


	# env_sensor = BME680()
	# env_sensor.start()
	# time.sleep(60)
	# env_sensor.stop()
