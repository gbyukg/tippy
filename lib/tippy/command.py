'''
The command package, used to parse command
'''

from tippy.parser import Parser
from tippy.plugin import Plugin
from tippy.errors import CommandError
from . import logger

class Command(object):
    '''
    Singleton class, using Parser class to parse instruction.
    '''

    def __init__(self):
        '''
        setup parser property to parse command

        Parser class will return a proper class object
        base on 'parser' key in the configuration file
        '''
        self.parser = Parser()
        self._permission_error = None
        self.cmd = None

    @property
    def permission(self):
        '''
        each command definition has particular execute permission
          - permission: who can run the command
          - channels: the command can be run in which channel.
        '''
        allow_runners = self.cmd.property.permission
        executor = self.cmd.client.executor.name
        if allow_runners and executor not in allow_runners:
            cmd = '{:s} {:s}'.format(
                self.cmd.current_command,
                self.cmd.subcommand
            )
            self._permission_error = 'you don\'t have permissiont to run this command'
            logger.warning(('the command [{:s}] can only be run by users: [{:s}], '
                            'current user is: {:s}'.format(
                                cmd,
                                str(allow_runners),
                                executor
                            )))
            return False
        # check if command can be run in current channel
        allow_channels = self.cmd.property.allow_channels
        channel = self.cmd.client.channel
        if allow_channels and channel not in allow_channels:
            cmd = '{:s} {:s}'.format(
                self.cmd.current_command,
                self.cmd.subcommand
            )
            self._permission_error = 'the command can not be run in this channel'
            logger.warning(('the command [{:s}] can only be run in channels: [{:s}], '
                            'current channel is: {:s}'.format(
                                cmd,
                                str(allow_channels),
                                channel
                            )))
            return False
        return True

    @permission.setter
    def permission(self):
        ''' permission can not be set manually '''
        raise Exception('permission can not be set')

    def __call__(self, cli_cmd, **kvargs):
        '''
        parse the command line(Slack message)
        the first string is considered as command.

        all the token except the first string(command) will be used as custom parameters
        merge command parameters from command line(Slack chat)
        each command yaml file should have a property named 'params' under 'property'
        used to store the default parameters, the parameters come from command line
        will overwrite the default parameters.
        '''
        logger.info('starting to run the command [{0:s}]'.format(cli_cmd))

        self.cmd = self.parser(cli_cmd)
        self.cmd.client = kvargs if kvargs is not None else {}
        '''
        if command struct has no permission property, or it is empty
        then we consider everyone has permission to run the command
        '''
        if self.permission is True:
            return Plugin(self.cmd).run()
        else:
            raise CommandError(self._permission_error)