import time
from rpi_control_center import GPIO_engine, rpi_usb

default_relay_config = {
        "1":{'name':'name1', 'pin':26, 'state':False},
        "2":{'name':'name2', 'pin':20, 'state':False},
        "3":{'name':'name3', 'pin':21, 'state':False},
}

if __name__ == '__main__':
    control_box = GPIO_engine.BulkUpdater(config_file = './relay_config.json',default_config =default_relay_config , refresh_rate = 1)
    control_box.start()

    ######### You can put any code because this function is non-blocking
    try:
        while True:
            print('test')
            time.sleep(5)
    except:
        print('hit')
        control_box.stop()
