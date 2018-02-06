'''
The base Plugin class
'''

import ssl
import logging
import importlib
from abc import ABCMeta, abstractmethod
from tippy.utils import *

logger = logging.getLogger(__name__)

__all__ = ['Plugin', 'PluginError', 'NoActionError', 'botcmd']

_action_list = {}

def botcmd(func):
    '''
    registe the plugin's function.
    each function defined in the plugins which want to be executed,
    need to register.
    '''
    _action_list.update({func.__name__: func})
    return func

class PluginError(Exception): pass
class NoActionError(Exception): pass

class Plugin(object, metaclass=ABCMeta):
    '''
    Base on the 'type' key in the command struct to get the proper Plugin object.
    This is a abstract class, each Plugin class should inherit this class.
    '''

    def __new__(cls, cmd):
        '''
        return the proper Plugin class

        using 'type' property in command struct
        to determine which PLUGIN we will use.
        '''
        plugin_type = cmd.property.type
        if plugin_type is None:
            errMsg = 'missing type key in command struct'
            logger.error(errMsg)
            raise PluginError(errMsg)
        plugin_type = plugin_type.lower()

        try:
            '''
            get the real Plugin class base on the 'type' attribute in the command struct
            e.g. import_module('.jenkins', 'packages')
            '''
            plugin_module = importlib.import_module('.{}'.format(plugin_type), __name__)
            plugin_kls = getattr(plugin_module, plugin_type.capitalize())
        except ModuleNotFoundError as e:
            logger.exception(e)
            raise PluginError("no such a Plugin module [{:s}]".format(plugin_module)) from e
        except AttributeError as e:
            logger.exception(e)
            raise PluginError("no such a Plugin class [{:s}]".format(plugin_kls)) from e
        else:
            return super().__new__(plugin_kls)

    def __init__(self, cmd):
        '''
        initialization for all Plugins
        '''
        self.config = TippyConfig()
        ssl._create_default_https_context = ssl._create_unverified_context
        self.cmd = cmd
        self.action_list = _action_list

    @abstractmethod
    def validate_property(self):
        ''' validate properies for each plugin '''

    @botcmd
    # 此处需要增加一个 logger
    def run(self):
        '''
        an abstract method, each Plugin should implement itself run function
        this is the entry function for all Plugins.
        '''
        try:
            _f = self.action_list[self.cmd.property.action]
        except KeyError:
            raise NoActionError(('no such Jenkins action named {:s} exist, '
                                 ('please check your command configuration.'.format(
                                     self.cmd.property.action
                                 ))))
        self.validate_property()
        return _f(self)

    @botcmd
    def help(self):
        return {
            'method': 'chat.postMessage',
            'options': {
                'attachments': [
                    {
                        "color": "#36a64f",
                        "title": self.cmd.description,
                        "text": self.cmd.help,
                        "author_name": self.cmd.client.executor.real_name,
                        "author_icon": self.cmd.client.executor.profile.image_32,
                        "footer": "Slack Bot",
                        "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
                    }
                ]
            }
        }