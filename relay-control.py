import sys
# import RPi.GPIO as GPIO
import threading
import time
import datetime
import json
import os.path
import glob

import relay_states as rs
from relay_states import Relay

#################### global variable
relay_config_file = './relay_config.json'


#
# Relay_Ch1 = 26
# Relay_Ch2 = 20
# Relay_Ch3 = 21





# def set_relay(relay, state = False):

if __name__ == '__main__':

    relay_config = rs.load_relay_config(relay_config_file)

    relays= rs.load_relay_objects(relay_config)

    # relays['1'].name = 'air_pump'

    print(relays)
