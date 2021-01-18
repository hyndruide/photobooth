import subprocess, time

DEFAULT_GATEWAY="192.168.42.1"
DEFAULT_DHCP_RANGE="192.168.42.2,192.168.42.254"
DEFAULT_INTERFACE="wlan0" # use 'ip link show' to see list of interfaces

def startDNS():
    # first kill any existing dnsmasq
    stopDNS()

    # build the list of args
    path = f"sudo"
    args = [path]
    args.append(f"-s")
    args.append(f"/usr/sbin/dnsmasq")
    args.append(f"--address=/#/{DEFAULT_GATEWAY}")
    args.append(f"--dhcp-range={DEFAULT_DHCP_RANGE}")
    args.append(f"--dhcp-option=option:router,{DEFAULT_GATEWAY}")
    args.append(f"--interface=wlan0")
    args.append(f"--keep-in-foreground")
    args.append(f"--bind-interfaces")
    args.append(f"--except-interface=lo")
    args.append(f"--conf-file")
    args.append(f"--no-hosts" )
    print(args)

    # run dnsmasq in the background and save a reference to the object
    ps = subprocess.Popen(args)
    # don't wait here, proc runs in background until we kill it.

    # give a few seconds for the proc to start
    time.sleep(2)
    print(f'Started dnsmasq, PID={ps.pid}')

def stopDNS():
    ps = subprocess.Popen("ps -e | grep ' dnsmasq' | cut -c 1-6", shell=True, stdout=subprocess.PIPE)
    pid = ps.stdout.read()
    ps.stdout.close()
    ps.wait()
    pid = pid.decode('utf-8')
    pid = pid.strip()
    if 0 < len(pid):
        print(f"Killing dnsmasq, PID='{pid}'")
        ps = subprocess.Popen(f"sudo kill -9 {pid}", shell=True)
        ps.wait()



