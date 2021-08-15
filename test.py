from rpi_control_center_pkg import state_updater as su





if __name__ == '__main__':
    control_box = su.BulkUpdater(config_file = './relay_config.json', default_config = default_relay_config , refresh_rate = 1)
    control_box.start()

    ######### You can put any code because this function is non-blocking
    try:
        while True:
            time.sleep(5)
    except:
        control_box.stop()
