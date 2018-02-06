import shlex
import importlib
import logging
from attrdict import AttrDefault
from abc import ABCMeta, abstractmethod
from tippy.utils import *
from tippy.errors import *

logger = logging.getLogger(__name__)

class Parser(object, metaclass=ABCMeta):
    '''
    Get the proper parser to parse the command base on the 'parser' key in the configuration file.
    You can also think of how we store our command information(YAML or MongoDB .etc.)
    Since we can only use one parser(YAML, or MongoDB etc.) during the entire runtime
    So this should be a singleton instance.
    '''
    _instance = None

    def __new__(cls):
        if not cls._instance:
            logger.debug('starting to initialize Parser class')
            config = TippyConfig()
            parser = config.parser
            # Parser module name = config.parser + parser, e.g.: yamlparser
            module_name = '.{:s}parser'.format(parser.lower())
            # the class name in the module is  config.parser + Parser, e.g.: YamlParser
            kls_name = "{}Parser".format(parser.capitalize())
            logger.debug('Initialize parser class [{:s}] in [{:s}] module'.format(kls_name, module_name))
            try:
                parser_module = importlib.import_module(module_name, __name__)
                parser_kls = getattr(parser_module, kls_name)
                cls._instance = super().__new__(parser_kls)
                logger.debug('Initialized new Parser object: {:s}.{:s}'.format(module_name, kls_name))
            except ModuleNotFoundError as e:
                logger.exception(e)
                raise ParserError("no such a Parser module [{:s}]".format(module_name)) from e
            except AttributeError as e:
                logger.exception(e)
                raise ParserError("no such a Parser class [{:s}]".format(kls_name)) from e

        return cls._instance
    
    @abstractmethod
    def parser_cmd(self, command): pass

    def __init__(self):
        self.conf = TippyConfig()
        self._attr = {}

    def __call__(self, cli_cmd):
        cli_list = shlex.split(cli_cmd)
        command = cli_list[0]

        # parse command file
        cmd_struct = self.parser_cmd(command)

        '''
        get subcommand
        in order to make argsparser works correctly,
        subcommand must appear in the cli command.
        add subcommand into cli_list
        '''
        try:
            if cli_list[1] != 'help' and cli_list[1] not in cmd_struct['commands'].keys():
                # if the subcommand not appeared in the CLI commnad
                # add 'default' as subcommand in cli_list as the second element
                cli_list.insert(1, 'default')
        except IndexError:
            # IndexError means there is only one element as main command in CLI command
            cli_list.append('default')
        finally:
            subcommand = cli_list[1]
            cmd_struct['commands'].setdefault(subcommand, {})

        cmd_property = dict(cmd_struct['commands'].get('_property', {}))
        cmd_property.update(cmd_struct['commands'][subcommand].get('property', {}))
        # set action to subcommand
        cmd_property.setdefault('action', subcommand)

        # get command params
        cmd_params = dict(cmd_struct['commands'][subcommand].get('params', {}))
        parser = TippyArgumentParser(
            prog=cli_list[0],
            description=cmd_struct.get('description')
        )
        subparsers = parser.add_subparsers()
        self.generate_cli_parser(subparsers, subcommand, cmd_params)

        if not cmd_params.get('_lock', False):
            cmd_params.update(vars(parser.parse_args(cli_list[1:])))

        cmd = AttrDefault(str, {})
        cmd.description = cmd_struct.get('description')
        cmd.property = cmd_property
        cmd.help = cmd_struct.get('help', command)
        cmd.command = command
        cmd.subcommand = subcommand
        cmd.params = cmd_params
        return cmd

    def generate_cli_parser(self, subparser, subcommand='default', params={}):
        sub_parser = subparser.add_parser(subcommand)
        for key, val in params.items():
            sub_parser.add_argument(
                '-' + key,
                default=val
            )