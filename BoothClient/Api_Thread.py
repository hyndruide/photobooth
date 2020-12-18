
from BoothClient.BoothClient import BoothClient
import os
from threading import Thread

class Api():
    def __init__(self):
        self.api = BoothClient()
        self.error = ''
        self.code = ''
        self.site = ''
        self.auth = False
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
                
                self.connect = True
        except ConnectionError as error:
            self.error = eval(repr(error))   
        self.sync_in_background()

    def wait_for_connexion(self):
        self.api.wait_for_first_connect()
        self.auth = True

    def sync_in_background(self):
        thread = Thread(target=self.upload_photos, daemon=True)
        thread.start()

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



if __name__ == "__main__":
    thread = Api_tread()
    thread.start()
    thread.join()
