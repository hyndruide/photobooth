from threading import Thread
from BoothClient.BoothClient import BoothClient
import os

class Api_tread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.api = BoothClient()
        self.flag_api=False
        self._flag_error=False
        self._flag_auth=False
        self._flag_connect=False
        self.connect = False
    def run(self):
        try:
            if self.api.connect() == False:
                try:
                    self.api.first_connect()
                except Exception as error:
                    self._flag_error= True
                    self.error = eval(repr(error))
                else :
                    self._flag_auth = True
                    self.api.wait_for_first_connect()
                    self._flag_connect=True
            else :
                self.connect = True
        except ConnectionError as error:
            self._flag_error= True
            self.error = eval(repr(error))   

        if self.connect:
            self.upload_photos()

    def upload_photos(self):
        listeFichiers = []
        for (rep, sousReps, fichiers) in os.walk("./photo/"):
            for fichier in fichiers:
                listeFichiers.append(os.path.join(rep, fichier))
            
        for filename in listeFichiers:
            self.send_photo(filename)

    def send_photo(self, filename):
        reponse = self.api.upload(filename)
        if 'id' in reponse:
            os.remove(filename)

    def flag_connect(self):
        return self._flag_connect 
    
    def shut_flag_connect(self):
        self._flag_connect = False

    def flag_auth(self):
        return self._flag_auth

    def flag_error(self):
        return self._flag_error
    
    def get_user_code(self):
        self._flag_auth = False
        return self.api.req['user_code']

    def get_site(self):
        return self.api.req['verification_uri']

    def get_error(self):
        self._flag_error = False
        return self.error
        

if __name__ == "__main__":
    thread = Api_tread()
    thread.start()
    thread.join()
