#!/usr/bin/env python-sirius

from siriushla import util
import getpass

pswd = getpass.getpass(prompt='Enter password to phyuser@linac-serv-nfs: ')

util.run_newprocess(
    [
        'sshpass', '-p', pswd, 'ssh', '-X',
        'phyuser@linac-serv-nfs', 'sh', '-c',
        '/home/sirius/work/opi/sirius-main.sh'],
    is_window=False)
