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

refresh_rate = 1

if __name__ == '__main__':

    rs.begin()
    relay_config = rs.load_relay_config(relay_config_file)
    relays= rs.load_relay_objects(relay_config)

    while True:
        rs.update_relay_states(dict_of_relays = relays, relay_config_file=relay_config_file)
        rs.print_all_relays(relays)
        time.sleep(refresh_rate)
    rs.stop()
