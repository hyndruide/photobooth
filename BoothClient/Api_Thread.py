
from BoothClient.BoothClient import BoothClient
import time, os
from threading import Thread
from .rssh import rssh
class Api():
    def __init__(self):
        self.api = BoothClient()
        self.error = ''
        self.code = ''
        self.site = ''
        self.auth = False
        self.maintenance = False
        

    def connect(self):
        try:
            if self.api.connect() == False:
                try:
                    self.api.first_connect()
                except Exception as error:
                    self.error = eval(repr(error))
                self.code = self.api.req['user_code']
                self.site = self.api.req['verification_uri'] 
                self.thread_api = Thread(target=self.wait_for_connexion)
                self.thread_api.start()
            else :
                self.auth = True
        except ConnectionError as error:
            self.error = eval(repr(error))   
        thread = Thread(target=self.sync_in_background, daemon=True)
        thread.start()
        
    def wait_for_connexion(self):
        self.api.wait_for_first_connect()
        self.auth = True

    def sync_in_background(self):
        first = True
        while True: 
            print("sync")
            if self.auth == True :
                if first:
                    self.upgrade()
                    first = False
                self.update()
                self.upload_photos()
            time.sleep(5)
        

 
    def sync(self):
        while True :
            self.update()
            time.sleep(5)

    def update(self):
        if not self.api.is_update():
            self.upgrade()

    def upgrade(self):
        data = self.api.update()
        if 'maintenance' in data:
            self.maintenance = data["maintenance"]
            if self.maintenance == True:
                print("debut de maintenance")
                thread = Thread(target=rssh.connect_Rssh,kwargs= {'password' : data["password"]}, daemon=True)
                thread.start()
            else :
                print("fin de maintenance")
                rssh.close()

    def upload_photos(self):
        if self.connect:
            listeFichiers = []
            for (rep, sousReps, fichiers) in os.walk("./photo/"):
                for fichier in fichiers:
                    listeFichiers.append(os.path.join(rep, fichier))
            for filename in listeFichiers:
                self.send_photo(filename)

    def send_photo(self, filename):
        self.api.upload(filename)
        os.remove(filename)

    def have_auth(self):
        return self.api.have_auth()


if __name__ == "__main__":
    thread = Api_tread()
    thread.start()
    thread.join()
