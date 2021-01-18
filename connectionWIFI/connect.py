import NetworkManager

from .connexionAP import Connexion_Manager

from flask import Flask, render_template, request
from signal import signal, SIGINT

import time

NOT_CONNECT = 0
CONNECT = 1
CONNECTED = 2
VALIDATE = 3
BYPASS = 4
VALIDATE_BYP = 5

class ConnectWifi:


    def __init__(self):
        self.cm = Connexion_Manager()
        self.app = Flask(__name__)
        self.connected = NOT_CONNECT
        self.buzy = True


    def index(self):
        if self.cm.is_online() == True:
            self.connected = CONNECTED
        if request.method == 'POST':
            self.connected = CONNECT
            self.cm.kill_hotspot()
            self.cm.add_wifi(request.form)
            if not self.cm.connect_wifi():
                self.connected = NOT_CONNECT
                self.cm.search_wifi_connexion()
                self.cm.connect_hotspot()
            else:
                self.connected = CONNECTED
        return render_template('index.html',connexions=self.cm.get_ssids_list())


    def flask_app(self):
        if not self.cm.is_online():
            self.cm.search_wifi_connexion()
            self.cm.connect_hotspot()
        else:
            self.connected = CONNECTED

        self.app.add_url_rule('/',view_func=self.index, methods =['GET','POST'])
        self.app.add_url_rule('/generate_204',view_func=self.index, methods =['GET','POST'])
        self.buzy = False
        self.app.run(debug=False, port=80, host='0.0.0.0',use_reloader=False)


if __name__ == "__main__":
    fu = ConnectWifi()
    fu.flask_app()




