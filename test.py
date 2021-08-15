from rpi_control_center_pkg import state_updater as su


if __name__ == '__main__':
    control_box = su.BulkUpdater(config_file = './relay_config.json', refresh_rate = 1)
    control_box.start()

    ######### You can put any code because this function is non-blocking
    # try:
    while True:
        print('test')
        time.sleep(5)
    # except:
    #     print('hit')
    #     control_box.stop()
