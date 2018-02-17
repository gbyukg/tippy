'''
Declare ChatBot engin
'''

import logging
import threading
from slackclient import SlackClient
from tippy.command import Command
from tippy.errors import EnginError

LOGGER = logging.getLogger(__name__)

class SlackEngin(object):
    '''
    ChatBot Slack Engin
    '''
    def __init__(self, slack_token):
        self.slack_token = slack_token
        self.sc = None

    def start(self):
        '''
        start up slack engin
        the entry point of the Slack
        '''

        self.sc = SlackClient(self.slack_token)
        if not self.sc.rtm_connect():
            LOGGER.critical('connect to Slack error')
            raise EnginError('connect to Slack error')

        while True:
            try:
                datas = self.sc.rtm_read()
            except ConnectionResetError as e:
                LOGGER.exception(e)
                self.sc.rtm_connect(reconnect=True)
            else:
                for data in datas:
                    # only the text begin with '!' will be considered as a command 
                    if data.get('type') == 'message' and data.get('text','').startswith('!'):
                        single_cmd = threading.Thread(target=self.execute, args=(data,))
                        single_cmd.start()

    def execute(self, data):
        '''
        starting to run the command
        '''
        cmd_text = data['text'][1:]
        executor = self.sc.api_call('users.info', user=data['user'])['user']
        extend_param = {
            'executor': executor,
            'channel': data['channel']
        }

        LOGGER.info(
            ('the command [{:s}] was triggered by user [{:s}] '
             'from Slack channel [{:s}]'.
             format(
                 cmd_text,
                 extend_param['executor']['name'],
                 extend_param['channel'])
            )
        )

        try:
            # showing Slack bot typing... message
            self.sc.server.send_to_websocket({
                "type": "typing",
                "channel":data['channel']
            })

            msg = Command()(cmd_text, **extend_param)
        except Exception as e:
            msg = {
                'options': {
                    'attachments': [{
                        "color": "#FF0000",
                        "title": "Error: {:s}".format(str(e)),
                        "author_name": executor['real_name'],
                        "author_icon": executor['profile']['image_32'],
                        "footer": "Slack Bot",
                        "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
                    }]
                }
            }
            LOGGER.exception(str(e))
        finally:
            result = self.sc.api_call(
                msg.get('method', 'chat.postMessage'),
                channel=data['channel'],
                **msg.setdefault('options', {})
                )
            if result['ok']:
                LOGGER.info('the command [{:s}] finished successfully'.format(cmd_text))
            else:
                LOGGER.error('the command [{:s}] failed'.format(cmd_text))
