'''
SSH Plugin file.
Library: paramiko (2.4.0)
'''

import base64
import paramiko
from io import StringIO
from ..plugin import Plugin, botcmd

class Ssh(Plugin):
    @botcmd
    def ssh_cmd(self):
        executor = self.cmd.client.executor
        ssh_server = self.cmd.params.ssh_server + self.cmd.property.ssh_server_suffix

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        private_key_stream = StringIO(self.cmd.property.ssh_key)
        private_key = paramiko.RSAKey.from_private_key(private_key_stream)
        private_key_stream.close()

        client.connect(
            hostname=ssh_server,
            username=self.cmd.params.ssh_user,
            port=self.cmd.params.ssh_port,
            pkey=private_key)
        stdin, stdout, stderr = client.exec_command(self.cmd.property.ssh_command)
        
        stdout_output = ''
        for line in stdout:
            stdout_output += line
        
        stderr_str = ''
        for err in stderr:
            stderr_str += err.strip('\n')
        
        client.close()
        
        if stderr_str:
            raise Exception("Run SSH command failed: [{:s}]".format(stderr_str))
        
        return {
            'method': 'chat.postMessage',
            'options': {
                'attachments': [
                    {
                        "color": '#36a64f',
                        "title": "Run the command `{:s}` at [{:s}] as user [{:}]".format(
                            self.cmd.property.ssh_command,
                            ssh_server,
                            self.cmd.params.ssh_user
                            ),
                        "text": stdout_output,
                        "author_name": executor.real_name,
                        "author_icon": executor.profile.image_32,
                        "footer": "Slack Bot",
                        "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
                    }
                ]
            }
        }
    
    def validate_property(self):
        return True