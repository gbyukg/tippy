import logging
import os
from tippy.utils import *
from tippy.engin import *

logger = logging.getLogger(__name__)

def init():
    # TippyConfig is a singleton instance
    # initialize config firstly, to make sure we will use the exactly same config instance  
    config = TippyConfig()
    config.section = 'PROD'

    # initialize logging module
    init_logging()
init()

slack_token = os.environ.get('SLACK_TOKEN')
print(slack_token)
SlackEngin(slack_token=slack_token).start()
