import shlex
import tippy.parser as parser
import tippy.command as command
from tippy.utils import *

def test():
    config = TippyConfig()
    config.section = 'PROD'
    # cli = "masking --MY_NAME=b01cxnp20072.ahe.pok.ibm.com --PR='123 abc'"
    cli = "masking help"
    cmd = command.Command()
    cmd(cli, channel='D8LMG232P', executor={'name': 'zzlzhang'})

import threading
from time import sleep, ctime

loops = [4, 2]

def loop(nloop, nsec):
    print("start loop", nloop, "at:", ctime())
    sleep(nsec)
    print("start loop", nloop, "done at:", ctime())

def main():
    print("starting at:", ctime())
    threads = []
    nloops = range(len(loops))
    
    for i in nloops:
        t = threading.Thread(target=loop, args=(i, loops[i]))
        threads.append(t)
    
    for i in nloops:
        threads[i].start()
    
    print("all DONE at:", ctime())

main()