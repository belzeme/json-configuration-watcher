import json
import os
import sys
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from pathlib import Path
# TODO Unit test
# TODO Functional test
#       - a new json file is created <- tested
#       - a json file is edited <- tested
#       - a bad json file is edited
#       - a non json file is added
#       - a json file is removed


""" Watch json configuration files.

    This module use the watchdog library to watch and store
    modification on json configuration files within a directory.
"""


class ConfigurationChangeHandler(FileSystemEventHandler):
    """ The handler call when a configuration file is edited

        Attributes:
            configuration - the file configurations
            hook - the function to call when an edition is catch
    """
    def __init__(self, conf_files, on_modified_hook):
        """ The ConfigurationChangeHandler constructor

        Args:
            conf_files - a list of configuration file to load
            on_modified_hook - the function to call when an edit is catch

        Raises:
            json.decoder.JSONDecodeError - when the given json file is corrupted
        """
        super().__init__()
        self.configuration = {}
        self.hook = on_modified_hook
        for conf_file in conf_files:
            try:
                self.load_configuration(conf_file)
            except json.decoder.JSONDecodeError as e:
                print(e)

    def load_configuration(self, path):
        """ Load the data from the given json file

            Args:
                path - the file path
        """
        with open(path) as conf_file:
            if path.name not in self.configuration:
                self.configuration[path.name] = {}
            self.configuration[path.name] = json.load(conf_file)

    def on_modified(self, event):
        """ Called when watchdogs emits a modified event

            Args:
                 event - a watchdog FileSystemEvent
        """
        path = Path(event.src_path)
        if path.is_file() and path.suffix == '.json':
            self.load_configuration(path)
            self.hook(self.configuration)


class ConfigurationManager:
    """ The Configuration Manager

        Attributes:
            conf_directory - the directory containing the configuration files to watch
            conf_files - the list of watched configuration file
            conf_observer - a watchdog observer
            conf_handler - a watchdog event handler
            observers - the list of observers
    """
    def __init__(self, conf_directory=os.path.join(sys.path[0], 'conf')):
        """ The ConfigurationManager constructor

            Args:
                conf_directory (string | sys.path[0]/conf)
            Raise:
                NotADirectoryError
        """
        self.conf_directory = Path(conf_directory)
        self.conf_files = []
        self.observers = []

        if not self.conf_directory.exists():
            raise NotADirectoryError('{} does not exist'.format(self.conf_directory))

        # Selects the files with a .json extension
        self.conf_files = self.conf_directory.glob('*.json')
        # Prepare the watchdog observer and handler
        self.conf_handler = ConfigurationChangeHandler(self.conf_files, self.notify)
        self.conf_observer = Observer()
        self.conf_observer.schedule(self.conf_handler, str(self.conf_directory))

    def start(self):
        """ Launch the observer thread """
        print('start watching {}'.format(self.conf_directory))
        self.conf_observer.start()

    def stop(self):
        """ Send a stop signal to the observer thread """
        print('stop watching {}'.format(self.conf_directory))
        self.conf_observer.stop()

    def join(self):
        """ Wait for the observer to finish its process """
        print('waiting {} observers to come back'.format(self.conf_directory))
        self.conf_observer.join()

    def observe(self, fn):
        """ Decorator that set the given function to be notified when the configuration data changes """
        self.observers.append(fn)
        return fn

    def notify(self, configuration_data):
        """ Notify the observers that the configuration data changed

            Args:
                configuration_data - the configuration files data
        """
        for observer in self.observers:
            observer(configuration_data)

    def configuration(self, conf_file=None):
        """ Return the configuration store in this manager

            Args:
                conf_file - the name of a configuration file or Nothing
            Note:
                if no conf_file has been given will return all the configurations from the configuration dir.
            Returns:
                A directory containing configuration data.
            Raise:
                KeyError if the given conf_file is not in the dir.
         """
        if conf_file is None:
            return self.conf_handler.configuration
        elif conf_file in self.conf_handler.configuration:
            return self.conf_handler.configuration[conf_file]
        else:
            raise KeyError('{} is not a configuration file from {}'.format(conf_file, self.conf_directory))
