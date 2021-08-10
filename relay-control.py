import sys
import RPi.GPIO as GPIO
import threading
import time
import datetime
import json
import os.path
import glob

#################### global variable
relay_config_file = './relay_config.json'



Relay_Ch1 = 26
Relay_Ch2 = 20
Relay_Ch3 = 21





# def set_relay(relay, state = False):

def load_config_json(config_file):

    if os.path.isfile(config_file):

        with open(config_file, "r") as f:
            result = json.load(f)

        return result

    else:
        return None

if __name__ == '__main__':

    if os.path.isfile(relay_config_file):
        load_config_json
