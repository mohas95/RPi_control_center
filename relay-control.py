import time
import os.path

import relay_states as rs
from relay_states import Relay

#################### global variable
relay_config_file = './relay_config.json'
refresh_rate = 1

if __name__ == '__main__':

    rs.begin(relay_config_file=relay_config_file, refresh_rate=refresh_rate)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        rs.stop()
        print('main done!')
