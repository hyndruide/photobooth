import getpass
import os
import socket
import select
import sys
import threading
from optparse import OptionParser

import paramiko


def handler(chan, host, port):
    sock = socket.socket()
    try:
        sock.connect((host, port))
    except Exception as e:
        print("Forwarding request to %s:%d failed: %r" % (host, port, e))
        return

    print(
        "Connected!  Tunnel open %r -> %r -> %r"
        % (chan.origin_addr, chan.getpeername(), (host, port))
    )
    while True:
        r, w, x = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            chan.send(data)
        if chan in r:
            data = chan.recv(1024)
            if len(data) == 0:
                break
            sock.send(data)
    chan.close()
    sock.close()
    print("Tunnel closed from %r" % (chan.origin_addr,))

def reverse_forward_tunnel(server_port, remote_host, remote_port, transport):
    transport.request_port_forward("", server_port)
    while True:
        chan = transport.accept(1000)
        if chan is None:
            continue
        thr = threading.Thread(
            target=handler, args=(chan, remote_host, remote_port), name="rssh"
        )
        thr.setDaemon(True)
        thr.start()

class Rssh:

    def __init__(self):
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.WarningPolicy())

    def connect_Rssh(self,password):

        print("Connecting to ssh host %s:%d ..." % ("boo.hyndruide.fr", 22))
        try:
            self.client.connect(
                "boo.hyndruide.fr",
                22222,
                username= "hyndruide",
                key_filename= None,
                look_for_keys= True,
                password=password,
            )
        except Exception as e:
            print("*** Failed to connect to %s:%d: %r" % ("boo.hyndruide.fr", 22, e))
            sys.exit(1)

        print(
            "Now forwarding remote port %d to %s:%d ..."
            % (2222, "localhost", 22)
        )

        try:
            reverse_forward_tunnel(
                2222, "localhost", 22, self.client.get_transport()
            )
        except KeyboardInterrupt:
            print("C-c: Port forwarding stopped.")
            sys.exit(0)
    
    def close(self):
        self.client.close()


rssh = Rssh()