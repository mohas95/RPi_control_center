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

def update_relay_states(dict_of_relays, relay_config_file):
    relay_config= rs.load_relay_config(relay_config_file)

    for relay_id, relay in dict_of_relays.items():

        if relay_config[relay_id]['name'] != relay.name:
            relay.name = relay_config[relay_id]['name']
        else:
            pass

        if relay_config[relay_id]['pin'] != relay.pin:
            relay.name = relay_config[relay_id]['name']
        else:
            pass

        if relay_config[relay_id]['state'] != relay.state:
            relay.name = relay_config[relay_id]['name']
        else:
            pass

def print_all_relays(dict_of_relays):

    for relay_id, relay in dict_of_relays.items():
        print(f'Relay{relay_id}: Name[{relay.name}], Pin[{relay.pin}], state[{relay.state}]')



if __name__ == '__main__':

    relay_config = rs.load_relay_config(relay_config_file)

    relays= rs.load_relay_objects(relay_config)

    # print(relays['1'].name)
    # relays['1'].name = 'air_pump'
    # print(relays['1'].name)

    while True:
        update_relay_states(dict_of_relays = relays, relay_config_file=relay_config_file)
        print_all_relays(relays)
        time.sleep(5)
