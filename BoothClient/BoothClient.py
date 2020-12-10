import hashlib
import os
from datetime import datetime, timezone
import time
import json
import requests
import random
import string


class BoothClient:
    def __init__(self, url='http://127.0.0.1:8000'):
        self.url = url
        self.token = None
        self.client_id = self._get_client_id()
        self.req = ''

    @staticmethod
    def _checksum(fp):
        hash = "sha1"
        pos = fp.tell()
        checksum = hashlib.new(hash, fp.read()).hexdigest()
        fp.seek(pos)
        return f"{hash}:{checksum}"

    @staticmethod
    def _get_random_string(length):
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str

    def _now(self, filename):
        dt = os.path.getctime(filename)
        dt = datetime.utcfromtimestamp(dt)
        dt = dt.replace(tzinfo=timezone.utc)
        return dt

    def upload(self, filename):
        if self.update_token() is False:
            return False
        with open(filename, "rb") as fp:
            data = {
                "name": os.path.basename(filename),
                "checksum": self._checksum(fp),
                "created_at": self._now(filename).isoformat(),
            }
            headers = {
                "Authorization": f"{self.token['token_type']} {self.token['access_token']}",
            }

            url = f"{self.url}/photo/upload"

            files = [("file", fp)]
            with requests.post(url, data=data, files=files, headers=headers) as r:
                if not r.ok:
                    raise ValueError(r.text)
                return r.json()

    def first_connect(self):
        url = f"{self.url}/photobooth/new"
        data = {
            "client_id": self.client_id,
        }
        try:
            with requests.post(url, data=data) as r:
                if not r.ok:
                    raise ValueError(r.text)
                self.req = r.json()
        except requests.exceptions.ConnectionError:
            raise ConnectionError("impossible de se connecter")

    def ask_first_connect(self):
        url = f"{self.url}/photobooth/wait"
        dt = {
                "grant_type": "",
                "client_id": self.client_id,
                "device_code": self.req['device_code']
            }
        with requests.post(url, data=dt) as r:
            if not r.ok:
                print(r.text)
                return True

            self.store_token(r.json())
            return False

    def wait_for_first_connect(self):
        while self.ask_first_connect():
            time.sleep(5)

    def connect(self):
        if self.update_token() is False:
            return False
        url = f"{self.url}/photobooth/connect"
        headers = {
            "Authorization": f"{self.token['token_type']} {self.token['access_token']}",
        }
        try:
            with requests.post(url, headers=headers) as r:
                if not r.ok:
                    raise ValueError(r.text)
                return r.json()      
        except requests.exceptions.ConnectionError:
            raise ConnectionError("impossible de se connecter")

    def store_token(self, token):
        with open('setting', 'r') as f1:
            setting_file = json.load(f1)
        setting_file['token'] = token
        with open('setting', 'w') as f1:
            json.dump(setting_file, f1)
        self.update_token()

    def _get_token(self):
        if os.path.isfile('setting'):
            with open('setting', 'r') as f1:
                setting_file = json.load(f1)
                if 'token' not in setting_file:
                    return None
                return setting_file['token']
        else:
            return None

    def _get_client_id(self):
        if os.path.isfile('setting'):
            with open('setting', 'r') as f1:
                client_id_value = json.load(f1)['client_id']
        else:
            client_id = {"client_id": "Bfut4sKXqR11KgNbxe4wXw2PF2nJAI4S"}
            with open('setting', 'w') as f1:
                json.dump(client_id, f1)
            client_id_value = client_id["client_id"]
        return client_id_value
        

    def update_token(self):
        token = self._get_token()
        if token is None:
            return False
        self.token = token


if __name__ == "__main__":
    photo = BoothClient()
    r = photo.first_connect()
    print(r)
    while photo.wait_first_connect(r):
        time.sleep(r['interval'])
    print("photomaton validé")
