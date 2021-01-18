
import NetworkManager, time, socket
import uuid

from .dhcpdnsmasq import startDNS, stopDNS

class Connexion_Manager:
    def __init__(self,interface ='wlan0',hotspot_name = 'PhotoBooth'):
        self.hotspot_id = 'PB'
        self.interface = interface
        self.hotspot_name = 'PhotoBooth'
        self.hotspot = {
        '802-11-wireless': {'band': 'bg',
                            'mode': 'ap',
                            'ssid': self.hotspot_name},
        'connection': {'autoconnect': False,
                        'id': self.hotspot_id,
                        'interface-name': 'wlan0',
                        'type': '802-11-wireless',
                        'uuid': str(uuid.uuid4())},
        'ipv4': {'address-data': [{'address': '192.168.42.1', 'prefix': 24}],
                'addresses': [['192.168.42.1', 24, '0.0.0.0']],
                'method': 'manual'},
        'ipv6': {'method': 'auto'}
        }
        self.wifi_id = ''
        self.ssids = []
        

    def _del_hotspot_connexion(self):
        # Find the hotspot connection
        try:
            connections = NetworkManager.Settings.ListConnections()
            connections = dict([(x.GetSettings()['connection']['id'], x) for x in connections])
            conn = connections[self.hotspot_id]
            conn.Delete()
        except Exception as e:
            print(f'stop_hotspot error {e}')
            return False
        time.sleep(5)
        return True

    def _del_all_connexion(self):
            # Get all known connections
            connections = NetworkManager.Settings.ListConnections()
            # Delete the '802-11-wireless' connections
            for connection in connections:
                if connection.GetSettings()["connection"]["type"] == "802-11-wireless":
                    connection.Delete()
            time.sleep(5)

    def _list_connexion(self):
        # bit flags we use when decoding what we get back from NetMan for each AP
        NM_SECURITY_NONE       = 0x0
        NM_SECURITY_WEP        = 0x1
        NM_SECURITY_WPA        = 0x2
        NM_SECURITY_WPA2       = 0x4
        NM_SECURITY_ENTERPRISE = 0x8

        ssids = [] # list we return

        for dev in NetworkManager.NetworkManager.GetDevices():
            if dev.DeviceType != NetworkManager.NM_DEVICE_TYPE_WIFI:
                continue
            for ap in dev.GetAccessPoints():

                # Get Flags, WpaFlags and RsnFlags, all are bit OR'd combinations 
                # of the NM_802_11_AP_SEC_* bit flags.
                # https://developer.gnome.org/NetworkManager/1.2/nm-dbus-types.html#NM80211ApSecurityFlags

                security = NM_SECURITY_NONE

                # Based on a subset of the flag settings we can determine which
                # type of security this AP uses.  
                # We can also determine what input we need from the user to connect to
                # any given AP (required for our dynamic UI form).
                if ap.Flags & NetworkManager.NM_802_11_AP_FLAGS_PRIVACY and \
                        ap.WpaFlags == NetworkManager.NM_802_11_AP_SEC_NONE and \
                        ap.RsnFlags == NetworkManager.NM_802_11_AP_SEC_NONE:
                    security = NM_SECURITY_WEP

                if ap.WpaFlags != NetworkManager.NM_802_11_AP_SEC_NONE:
                    security = NM_SECURITY_WPA

                if ap.RsnFlags != NetworkManager.NM_802_11_AP_SEC_NONE:
                    security = NM_SECURITY_WPA2

                if ap.WpaFlags & NetworkManager.NM_802_11_AP_SEC_KEY_MGMT_802_1X or \
                        ap.RsnFlags & NetworkManager.NM_802_11_AP_SEC_KEY_MGMT_802_1X:
                    security = NM_SECURITY_ENTERPRISE

                #print(f'{ap.Ssid:15} Flags=0x{ap.Flags:X} WpaFlags=0x{ap.WpaFlags:X} RsnFlags=0x{ap.RsnFlags:X}')

                # Decode our flag into a display string
                security_str = ''
                if security == NM_SECURITY_NONE:
                    security_str = 'NONE'
        
                if security & NM_SECURITY_WEP:
                    security_str = 'WEP'
        
                if security & NM_SECURITY_WPA:
                    security_str = 'WPA'
        
                if security & NM_SECURITY_WPA2:
                    security_str = 'WPA2'
        
                if security & NM_SECURITY_ENTERPRISE:
                    security_str = 'ENTERPRISE'

                entry = {"ssid": ap.Ssid, "security": security_str}

                # Don't add duplicates to the list, issue #8
                if ssids.__contains__(entry):
                    continue

                # Don't add hotspot in list
                if ap.Ssid == 'PB':
                    continue

                ssids.append(entry)

        print(f'Available SSIDs: {ssids}')
        self.ssids =  ssids

    def _add_hotspot(self):
        NetworkManager.Settings.AddConnection(self.hotspot)

    def _add_wifi_password(self,ssid,password):
        idcon = 'WIFICON'
        connection = {
        '802-11-wireless': {'mode': 'infrastructure',
                            'security': '802-11-wireless-security',
                            'ssid': ssid},
        '802-11-wireless-security': {'auth-alg': 'open', 'key-mgmt': 'wpa-psk', 'psk': password},
        'connection': {'id': idcon,
                        'type': '802-11-wireless',
                        'uuid': str(uuid.uuid4())},
        'ipv4': {'method': 'auto'},
        'ipv6': {'method': 'auto'}
        }
        NetworkManager.Settings.AddConnection(connection)
        time.sleep(5)
        self.wifi_id = idcon 

    def _add_wifi_open(self,ssid):
        idcon = 'WIFICONOPEN'
        # No auth, 'open' connection.
        connection = {
            '802-11-wireless': {'mode': 'infrastructure',
                                'ssid': ssid},
            'connection': {'id': idcon,
                           'type': '802-11-wireless',
                           'uuid': str(uuid.uuid4())},
            'ipv4': {'method': 'auto'},
            'ipv6': {'method': 'auto'}
        }
        NetworkManager.Settings.AddConnection(connection)
        time.sleep(5)
        self.wifi_id = idcon 


    def _add_wifi_entreprise(self,ssid,user,password):
        idcon = 'WIFICONENTREPRISE'
        # This is what we use for "MIT SECURE" network.
        connection = {
            '802-11-wireless': {'mode': 'infrastructure',
                                'security': '802-11-wireless-security',
                                'ssid': ssid},
            '802-11-wireless-security': 
                {'auth-alg': 'open', 'key-mgmt': 'wpa-eap'},
            '802-1x': {'eap': ['peap'],
                       'identity': user,
                       'password': password,
                       'phase2-auth': 'mschapv2'},
            'connection': {'id': idcon,
                           'type': '802-11-wireless',
                           'uuid': str(uuid.uuid4())},
            'ipv4': {'method': 'auto'},
            'ipv6': {'method': 'auto'}
        }
        NetworkManager.Settings.AddConnection(connection)
        time.sleep(5)
        self.wifi_id = idcon 


    def _start_wifi(self,conn_id):
        connections = NetworkManager.Settings.ListConnections()
        connections = dict([(x.GetSettings()['connection']['id'], x) for x in connections])
        conn = connections[conn_id]
        ctype = conn.GetSettings()['connection']['type']
        dtype = {'802-11-wireless': NetworkManager.NM_DEVICE_TYPE_WIFI}.get(ctype,ctype)
        devices = NetworkManager.NetworkManager.GetDevices()

        for dev in devices:
            if dev.DeviceType == dtype:
                break
        else:
            print(f"connect_to_AP() Error: No suitable and available {ctype} device found.")

        # And connect
        time.sleep(5)
        NetworkManager.NetworkManager.ActivateConnection(conn, dev, "/")
        print(f"Activated connection={conn_id}.")
        time.sleep(10)

        print(f'Waiting for connection to become active...')
        loop_count = 0
        while dev.State != NetworkManager.NM_DEVICE_STATE_ACTIVATED:
            time.sleep(1)
            loop_count += 1
            if loop_count > 30: # only wait 30 seconds max
                break

        if dev.State == NetworkManager.NM_DEVICE_STATE_ACTIVATED:
            print(f'Connection {conn_id} is live.')
            return True
        return False

    def _have_active_internet_connection(self,host="8.8.8.8", port=53, timeout=2):
        try:
            socket.setdefaulttimeout(timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, 25, b'wlan0')
            s.connect((host, port))
            print("Connecté")
            return True
        except Exception as e:
            print(f"Exception: {e}")
            print("Pas connecté")
            return False
   
    def connect_hotspot(self):
        self._add_hotspot()
        self._start_wifi(self.hotspot_id)
        startDNS()
    
    def search_wifi_connexion(self):
        self._del_all_connexion()
        time.sleep(5)
        self._list_connexion()

    def get_ssids_list(self):
        return self.ssids

    def kill_hotspot(self):
        self._del_hotspot_connexion()
        stopDNS()
    
    def add_wifi(self,profil):
        if profil['security'] == 'WEP' or profil['security'] == 'WPA' or profil['security'] == 'WPA2':
            self._add_wifi_password(profil['ssid'],profil['password'])
        if profil['security'] == 'NONE':
            self._add_wifi_open(profil['ssid'])
        if profil['security'] == 'ENTERPRISE':
            self._add_wifi_entreprise(profil['ssid'],profil['user'],profil['password'])

    def connect_wifi(self):
        if self._start_wifi(self.wifi_id) == True:
            return self._have_active_internet_connection()
    
    def is_online(self):
        return self._have_active_internet_connection()




