import requests
import time
from pyzabbix import ZabbixAPI
from ..plugin import Plugin, PluginError, botcmd

class Zabbix(Plugin):
    def _login_zabbix(self):
        '''
        initialize Zabbix author
        use a custom session to get the zabbix login information
        update ZabbixAPI AUTH use this session so we can use ZabbixAPI directlly. 
        '''
        # cmd_property = self.cmd.property
        loginurl = self.cmd.property.server + "/index.php"
        # Data that needs to be posted to the Frontend to log in
        logindata = {
            'autologin' : '1',
            'name' : self.cmd.property.owner,
            'password' : self.cmd.property.token,
            'enter' : 'Sign in'
        }
        # We need to fool the frontend into thinking we are a real browser
        headers = {
            'User-Agent' :'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0',
            'Content-type' : 'application/x-www-form-urlencoded'
        }

        # setup a session object so we can reuse session cookies
        self.session=requests.Session()
        self.session.post(loginurl, params=logindata, headers=headers, verify=False)

        self.zapi = ZabbixAPI(self.cmd.property.server)
        self.zapi.auth = self.session.cookies['zbx_sessionid']

    @botcmd
    def graph(self):
        '''
        generate the particular graph under the given host
        then send the picture into Slack
        '''
        self._login_zabbix()
        # params = self.cmd.params
        host_graphs = self.zapi.graph.get(output='extend', expandName=True, filter={'host': self.cmd.params.graph_host})
        for graph in host_graphs:
            if graph['name'] == self.cmd.params.graph:
                graph['period'] = self.cmd.params.get('period', 3600)
                graph['stime'] = time.time()-graph['period']
                current_graph = graph
                break

        if current_graph is None:
            raise PluginError('no such zabbix graph')

        graph_url = ('{:s}/chart2.php?graphid={g[graphid]}' 
                    '&period={g[period]}'
                    '&width={g[width]}'
                    '&height={g[height]}'
                    '&stime={g[stime]}'.format(self.cmd.property.server, g=current_graph))
        graphreq = self.session.get(graph_url,verify=False)

        return {
            'method': 'files.upload',
            'options': {
                'file': graphreq.content,
                'filename': self.cmd.params.graph,
                'title': '{:s} for {:s}'.format(self.cmd.params.graph, self.cmd.params.graph_host),
                'channels': self.cmd.client.channel,
            }
        }

    def validate_property(self):
        validated_fields = ('server', 'owner', 'token')
        for field in validated_fields:
            if not self.cmd.property[field]:
                raise Exception('property {:s} is not set'.format(field))