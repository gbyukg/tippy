'''
utils package
'''

import os
import argparse
import logging
from logging.config import dictConfig
from configparser import ConfigParser

__all__ = ['MetaSingleton', 'TippyConfig', 'init_logging', 'TippyArgumentParser']
LOGGER = logging.getLogger(__name__)

class MetaSingleton(type):
    ''' metaclass, used to create signle class'''
    _instances = {}
    def __call__(cls, reload=False, *args, **kwargs):
        if reload is True or cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, \
                cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class TippyConfig(object, metaclass=MetaSingleton):
    """
    Configuration object
    It's a singleton pattern
    """

    _root_dir = os.path.dirname(os.getcwd())
    _configuratinos = {}
    _config_path = '{:s}/configs/configuration.ini'.format(_root_dir)
    _init_config = {
        'root_dir': _root_dir
    }

    def __init__(self):
        self.config = ConfigParser(self._init_config)
        self.config.read(self._config_path)

    @property
    def section(self):
        ''' set which config section will be used '''
        return self._configuratinos.get('section')

    @section.setter
    def section(self, section):
        # Only one configuration section can be used during the entire life cycle
        # That means section is used for different environment.
        if self._configuratinos.get('section') is None:
            self._configuratinos['section'] = section
            #sectionObj = self.config[section]
            for name, value in self.config.items(section):
                self.__dict__[name] = value
        elif section != self._configuratinos.get('section'):
            print('Warning!!!!!!')

def init_logging():
    ''' initilaze logger '''
    config = TippyConfig()

    dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - [%(levelname)s] %(name)s [%(module)s.%(funcName)s:%(lineno)d]: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            }
        },
        'handlers' : {
                'file': {
                    'level': logging.DEBUG,
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'standard',
                    'filename': config.log_file,
                    'maxBytes': 1024,
                }
        },
        'loggers': {
                '__main__': {
                    'handlers' : ['file'],
                    'level': config.log_level,
                    'propagate': False,
                },
        },
        'root': {
                'level': config.log_level,
                'handlers': ['file']
        },
    })


class TippyArgumentParser(argparse.ArgumentParser):
    '''
    subclass of argparse.ArgumentParser
    used to handle errors
    '''
    def error(self, message):
        ''' we need to raise a exception when some parser error is occurring. '''
        raise Exception(message)
