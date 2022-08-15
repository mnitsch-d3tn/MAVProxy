#!/usr/bin/env python
'''
DTN Module
D3TN GmbH, August 2022
'''

import os
import os.path
import sys
from pymavlink import mavutil
import errno
import time
import threading

from MAVProxy.modules.lib import mp_module
from MAVProxy.modules.lib import mp_util
from MAVProxy.modules.lib import mp_settings

from ud3tn_utils.aap import AAPTCPClient
from ud3tn_utils.aap.aap_message import AAPMessageType


class dtn(mp_module.MPModule):
    def __init__(self, mpstate):
        """Initialise module"""
        super(dtn, self).__init__(mpstate, "dtn", "")
        self._stop = threading.Event()

        #self.dtn_settings = mp_settings.MPSettings(
        #    [ ('ip:port', str, False),
        #  ]) 
        self.add_command('dtn', self.cmd_dtn, "dtn module", ['start', 'stop'])

    def usage(self):
        '''show help on command line options'''
        return "Usage: dtn start"

    def cmd_dtn(self, args):
        '''control behaviour of the module'''
        if len(args) == 0:
            print(self.usage())
        elif args[0] == "start":
            self._aap_recv_thread.start()
            #self._aap_recv_thread = threading.Thread(target=self._aap_recv, daemon=True)
        elif args[0] == "stop":
            self._stop.set()
        else:
            print(self.usage())

    def _aap_recv(self):
        with AAPTCPClient(address=('127.0.0.1', 4242)) as aap_client:
            aap_client.register('mavproxy')
            while not self._stop.isSet():
                msg = aap_client.receive()
                print(msg)
                if msg and msg.msg_type == AAPMessageType.RECVBUNDLE:
                    cmd, *args = msg.payload.decode().split()
                    print(f"Received Command: {payload}")
                    if cmd == 'arm':
                        self.master.arducopter_arm()
                        self.master.motors_armed_wait()
                    elif cmd == 'disarm':
                        self.master.arducopter_disarm()
                        self.master.motors_disarmed_wait()
                    elif cmd == 'position':
                        print(args)
                else:
                    print("Received message is not a bundle.")


    def mavlink_packet(self, m):
        '''handle mavlink packets'''
        #print(m)

def init(mpstate):
    '''initialise module'''
    return dtn(mpstate)
