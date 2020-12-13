
from BoothClient.BoothClient import BoothClient
import os
from threading import Thread

class Api():
    def __init__(self):
        self.api = BoothClient()
        self.error = ''
        self.auth = ''
        self.connect = False

    def connect(self):
        try:
            if self.api.connect() == False:
                try:
                    self.api.first_connect()
                except Exception as error:
                    self.error = eval(repr(error))
                return (self.api.req['usercode'],self.api.req['verification_uri'])
                
            else :
                self.connect = True
        except ConnectionError as error:
            self.error = eval(repr(error))   
        self.sync_in_background()

    def wait_for_connexion(self):
        self.api.wait_for_first_connect()
        self.connect = True

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
