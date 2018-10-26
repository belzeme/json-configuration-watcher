import logging
import time

from configuration_manager import ConfigurationManager

conf_manager = ConfigurationManager()
module_params = {}


@conf_manager.observe
def update_configuration(new_configuration):
    print('updating new configuration')
    global module_params
    module_params = new_configuration


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    module_params = conf_manager.configuration()
    print(module_params)
    conf_manager.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        conf_manager.stop()
        conf_manager.join()


