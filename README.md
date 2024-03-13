This package provides additional suite of python based rpi abstraction for handling rpi hardware and data control. The package currently includes an abstraction layer and API engine for the RPi.GPIO package for python, which allows for multi-process and non-blocking control of GPIO pins. The package also includes a module for handling usb mass storage device mounting, data dumping, and unmounting,and other data handling. Finally the Package also includes a module for common sensors.

This package provides an abstraction layer and API engine for the [RPi.GPIO](https://pypi.org/project/RPi.GPIO/) package for python, which allows for multi-process and **non-blocking** control of GPIO pins.
With this package you can start the GPIO Engine, and control the output pins for relay control/ actuation using a json configuration files, while your code performs other
operations. This allows for relative __real time control<sup>*</sup>__ of the GPIO pins(~<1s scale). This package also provides real-time api of the status for external logging or
communication.Using the JSON protocol for the api we can allow for user control and information logging. For now this package only handles GPIO output but will feature
input control in the near future.



___*Note:___ While this package provides multi-process control of the GPIO pins for near real-time control, jitter can vary considerably due to the nature of Linux OS and
python's garbage collection. For now refresh rate is by default set to 1 second to mitigate issue of jitter to a known scale, but we cannot guarantee performance if  refresh rate is set to 0.

- Documentation: *Coming soon*
- [Github](https://github.com/moha7108/RPi_control_center)

## Installation

- pip
```shell
pip install RPI-control-center
```
- source
```shell
git clone https://gitlab.com/moha7108/rpi-control-center.git
cd rpi-control-center
pip install -r requirements.txt
```

## Example Usage
### Control Scripts
#### Controlling relays
```python
import time
from rpi_control_center import controls

relay_config = {
        "relay1":{'pin':26, 'state':False, 'config':'no'},
        "relay2":{'pin':20, 'state':False, 'config':'no'},
        "relay3":{'pin':21, 'state':False, 'config':'no'},
}

relay_group1 = controls.relay_engine( relay_config=relay_config,
                             label='test_relays', 
                             api_dir='./api/', 
                             log_dir='./log/',
                             refresh_rate=1)

relay_group1.start()


######### You can put any code because this function is non-blocking
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
```

#### USB Mass Storage Script
```python
import time, os
from rpi_control_center import rpi_usb

storage_devices = rpi_usb.get_devices(True)
print(storage_devices)

for dev in storage_devices:
    dev('test.txt')
    time.sleep(5)
    os.system(f'sudo ls {dev.mnt}')
    dev.umnt_usb()
    os.system(f'sudo ls /mnt')
```

#### CSV Handling Script
```python
from rpi_control_center.data import csv_handler

test_data = {'hello': 13, 'poop':'34013'}

test_csv = csv_handler(filename='test_data')
test_csv(test_data)

print(test_csv.data_files)
print(test_csv.writing_to)
print(test_csv.total_size)
```

### Sensor Monitoring scripts
```python
from rpi_sensor_monitors import monitors


env_sensor = monitors.BME680()
env_sensor.start()
time.sleep(60)
env_sensor.stop()
```

## Hardware and drivers

### List of Compatible Raspberry Pi boards
- [Raspberrypi 3B+](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)
- [Raspberrypi Zero 2W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/)

### List of Compatible Sensors

- BEM680
- any Ultrasonic sensor


## Feedback

All kinds of feedback and contributions are welcome.

- [Create an issue](https://github.com/moha7108/RPi_control_center/issues)
- Create a pull request
- Reach out to @moha7108

## Contributors

- Mohamed Debbagh
  - [GitLab](https://gitlab.com/moha7108/), [Github](https://github.com/moha7108/), [Twitter](https://twitter.com/moha7108)

## Change Log
### 0.2.3
- Move relay controlling to controls module and simplify code
- CO2 Sensor compatability

### 0.2.2 
- add ultrasonic sensor monitor
    - get sensor reading from object directly
- add am2420 sensor class
- add dual camera (VERY SPECIFIC USECASE)
- change package architecture to include control module
- add pwm to control module
### 0.2.1
- add data module with csv handler class to the rpi_control_center package
-
### 0.2.0
- addition of rpi_monitors module for sensor interfacing (currently only DFRobot_BME680)
- add dependancies (smbus, spidev)
### 0.1.3
- add rpi_usb module for usb mass storage handling
### 0.1.2
- fix minor error in test and example code
### 0.1.1
- Change host to github for better community issue tracking and documentation, functionally the same as previous version
- gitlab will be used as a mirror
### 0.1.0
- Logging via logzero, ability to suppress debug level logs when debug_mode is off
- create log and api folders when they do not exist
- all previous versions are pre release, this is the first working release

### Packaging Notes
- source venv/bin/activate
- python setup.py sdist bdist_wheel
- twine upload dist/*  or twine upload --repository-url https://test.pypi.org/legacy/ dist/*