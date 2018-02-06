import yaml
from . import Parser, logger
from tippy.errors import ParserError

class YamlParser(Parser):
    ''' using to parse yaml file '''
    def parser_cmd(self, cmd):
        """ parse command from yaml file, and return a dictionary"""
        command_file = '{:s}/{:s}.yaml'.format(self.conf.command_dir, cmd)
        try:
            with open(command_file, 'r') as stream:
                cmd_struct = yaml.load(stream)
        except FileNotFoundError as e:
            logger.exception(e)
            raise ParserError('no such command [{:s}] found'.format(cmd)) from e
        except yaml.YAMLError as e:
            logger.exception(e)
            raise ParserError("syntax error in {:s}.yaml file".format(cmd)) from e
        except Exception as e:
            logger.exception(e)
            raise ParserError(str(e)) from e
        else:
            return cmd_struct