This package provides an abstraction layer and API engine for the [RPi.GPIO](https://pypi.org/project/RPi.GPIO/) package for python, which allows for multi-process and **non-blocking** control of GPIO pins.
With this package you can start the GPIO Engine, and control the output pins for relay control/ actuation using a json configuration files, while your code performs other
operations. This allows for relative __real time control<sup>*</sup>__ of the GPIO pins(~<1s scale). This package also provides real-time api of the status for external logging or
communication.Using the JSON protocol for the api we can allow for user control and information logging. For now this package only handles GPIO output but will feature
input control in the near future.

___*Note:___ While this package provides multi-process control of the GPIO pins for near real-time control, jitter can vary considerably due to the nature of Linux OS and
python's garbage collection. For now refresh rate is by default set to 1 second to mitigate issue of jitter to a known scale, but we cannot guarantee performance if  refresh rate is set to 0.

- Documentation: *Coming soon*
- [Github](https://github.com/moha7108/RPi_control_center)
- [GitLab](https://gitlab.com/moha7108/rpi-control-center)

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
### GPIO Control Script
```python
import time
from rpi_control_center import GPIO_engine

## please note configuration must be in this format incase of missing file, file corruption, and other errors
default_relay_config = {
        "1":{'name':'name1', 'pin':26, 'state':False},
        "2":{'name':'name2', 'pin':20, 'state':False},
        "3":{'name':'name3', 'pin':21, 'state':False},
}

control_box = GPIO_engine.BulkUpdater(
                                        config_file = './relay_config.json',
                                        api_dir = './api',
                                        default_config = default_relay_config,
                                        refresh_rate = 1
                                      )
control_box.start()
######### You can put any code because this function is non-blocking
try:
    while True:
        time.sleep(5)
except:
    control_box.stop()
```

### Configuration/ API Files
- pin configuration file _(ie. relay_config.json, this example is a 3 GPIO pin configuration, once instantiated the state can be changed in the file and the change will be reflected in the gpio pin)_
```json
{
    "1": {
        "name": "name1",
        "pin": 26,
        "state": false
    },
    "2": {
        "name": "name2",
        "pin": 20,
        "state": false
    },
    "3": {
        "name": "name3",
        "pin": 21,
        "state": false
    }
}
```

- API file _(json file that is constantly updated with the status of a certain pin)_
```json
{
    "id": "1",
    "name": "name1",
    "pin": 26,
    "status": false,
    "last updated": "2021/08/16 17:03:49"
}
```

### USB Mass Storage Script
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

### Sensor Monitoring
```python
from rpi_sensor_monitors import monitors


env_sensor = monitors.BME680()
env_sensor.start()
time.sleep(60)
env_sensor.stop()
```


## Hardware and drivers

### Hardware

- [Raspberrypi 3B+](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)
  - OS: Rasbian Buster +

### System Libraries

- [waveshare guide](https://www.waveshare.com/wiki/Libraries_Installation_for_RPi)

``` shell
cd
sudo apt update
sudo apt list --upgradeable
sudo apt ugrade
sudo apt autoremove

sudo apt-get install wiringpi
wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb
gpio -v
sudo apt-get install libopenjp2-7 -y
sudo apt-get install libatlas-base-dev -y
sudo apt install libtiff -y
sudo apt install libtiff5 -y
sudo apt-get install -y i2c-tools
```

## Feedback

All kinds of feedback and contributions are welcome.

- [Create an issue](https://github.com/moha7108/RPi_control_center/issues)
- Create a pull request
- Reach out to @moha7108

## Contributors

- Mohamed Debbagh
  - [GitLab](https://gitlab.com/moha7108/), [Github](https://github.com/moha7108/), [Twitter](https://twitter.com/moha7108)

## Change Log
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
