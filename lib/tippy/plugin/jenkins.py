'''
SlackBot Plugin file.
'''

import jenkins
from ..plugin import Plugin, botcmd

class Jenkins(Plugin):
    '''
    The method can be called by bot:
      - build: trigger Jenkins job
      - help: print help message
    '''

    @botcmd
    def build(self):
        ''' trigger Jenkins job '''
        jenkins_server = jenkins.Jenkins(
            self.cmd.property.server,
            username=self.cmd.property.owner,
            password=self.cmd.property.token)

        jenkins_server.build_job(
            self.cmd.property.job_name,
            parameters=self.cmd.params
        )

        executor = self.cmd.client.executor

        return {
            'method': 'chat.postMessage',
            'options': {
                'attachments': [
                    {
                        "color": "#36a64f",
                        "title": "The jenkins job {:s} has been triggered".format(self.cmd.property.job_name),
                        "title_link": "{:s}/job/{:s}".format(self.cmd.property.server, self.cmd.property.job_name),
                        "author_name": executor.real_name,
                        "author_icon": executor.profile.image_32,
                        "footer": "Slack Bot",
                        "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
                    }
                ]
            }
        }

    def validate_property(self):
        validated_fields = ('server', 'owner', 'token')
        for field in validated_fields:
            if not self.cmd.property[field]:
                raise Exception('property {:s} is not set'.format(field))
