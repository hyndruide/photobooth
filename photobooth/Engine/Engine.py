import pygame
import json
from photobooth.Engine.Vue.Vue import Vue
from photobooth.Engine.Camera.Camera import Camera
from photobooth.Engine.Camera.Preview import Preview
from photobooth.Engine.Vue.Fonts import Fonts
from photobooth.Engine.Vue.Template import Templates_Collection
from BoothClient.Api_Thread import Api
from .State import State
from connectionWIFI.connect import (
    ConnectWifi,
    NOT_CONNECT,
    CONNECT,
    CONNECTED,
    VALIDATE,
    BYPASS,
    VALIDATE_BYP
)

from threading import Thread
import numpy

#TODO 
    # def afficher_no_connexion(self):
    #     self.fenetre.fill(self.colour_bg)
    #     info = paragraph("Pas de connexion internet\nles photos seront stocké\nelles seront envoyées\nà la prochaine connection", self.cta_font, WHITE, "center")
    #     self.blit_window(info, "center", "top")
    #     info = paragraph("appuyer à droite\npour passer", self.error_font, ORANGE, "center")
    #     self.blit_window(info, "right", "bottom")
    #     info = paragraph("appuyer à gauche\npour reconnecter", self.error_font, ORANGE, "left")
    #     self.blit_window(info, "left", "bottom")
    #     pygame.display.flip()


class Engine:
    def __init__(self,surface):
        self.fonts = Fonts()
        self.surface = surface
        self.running = True
        self._load_engine_file()
        self._need_update = False
        self.api = Api()
        self.templates_collection = Templates_Collection()
        self.con_wifi = ConnectWifi()
        self.thread_wifi = Thread(target=self.con_wifi.flask_app, daemon=True)
        self.thread_wifi.start()
        self.var = None
        self.camera = pygame.camera.Camera("/dev/video0",(1280,720), "RGB")
        self.state =State(self.sequences,self.sequences_api,self._prerender)
        self.state.restart()

    def _load_engine_file(self):
        with open('photobooth/json/sequence.json', 'r',encoding='utf-8') as file:
            self.data = json.load(file)
        self.sequences = self.data['sequence']
        self.sequences_api = self.data['api']

    # @property
    # def state(self):
    #     return self._state

    # @state.setter
    # def state(self, value):
    #     self._state = value
    #     if self._state <= 0:
    #         self._state = 0
    #     if self._state >= len(self.sequences)-1:
    #         self._state = len(self.sequences)-1
    #     self._prerender()

    def _prerender(self,sequence):
        template = self.templates_collection.load(sequence["vue"])

        self._launch_timer()
        self.type = sequence['type']
        self.screen_sequence = sequence
        if "timer_reset" in sequence:
            self.timer_reset = sequence["timer_reset"]
        else:
            self.timer_reset = False
        if 'always_update' in sequence:
            self.always_update = sequence['always_update']
        else:
            self.always_update = False

        if self.type == "screen_text":
            vue = Vue(self.surface,template,self.fonts)
            vue.set_var(self.var)
            self.var = None
        elif self.type == "camera":
            vue = Camera(self.surface,template,self.fonts,camera = self.camera)
        elif self.type == "preview":
            vue = Preview(self.surface,template,self.fonts)
            vue.load_photo(self.screen_data)

        self.screen = vue
        self.screen.load_render(self.screen_sequence)
        self._need_update = True

    def _render(self):
        if self._need_update or self.always_update:
            self.screen.make_render()
            pygame.display.flip()
            self._need_update = False

    def _restart(self):
        self._launch_timer()
        self.state.restart()

    def _launch_timer(self):
        self.tick = pygame.time.get_ticks()

    def _check_status_vue(self):
        if self.screen.is_done() :
            self.screen_data = self.screen.get_data()
            if type(self.screen_data) == str:
                if self.con_wifi.connected == VALIDATE:
                    thread = Thread(target=self.api.send_photo, args=("./photo/" + self.screen_data,), daemon=True)
                    thread.start()
            self.state.next()

    def _check_timer(self):
        if self.timer_reset is not False:
            seconds=(pygame.time.get_ticks()-self.tick)/1000 
            time_left = self.timer_reset - seconds
            if time_left < 0:
                self._restart()

    def next(self):
        self.screen.next()

    def prev(self):
        if self.screen.prev():
             self.state.back()

    def _check_connexion_api(self):
        if self.con_wifi.buzy == True:
            self.state.popup("wait_connexion")
        else :
            self.state.rm_popup("wait_connexion")
        if not self.con_wifi.buzy and self.con_wifi.connected == NOT_CONNECT :
            if self.api.have_auth():
                self.state.popup("Pas_connexion_bypass")
                self.con_wifi.connected = VALIDATE_BYP
            else:
                self.state.popup("Pas_connexion")
        if self.con_wifi.connected == CONNECT :
            self.state.popup("connexion")
        if self.con_wifi.connected == CONNECTED:
            self.con_wifi.connected = VALIDATE
            thread_api = Thread(target=self.api.connect)
            thread_api.start()
            self.state.rm_popup("connexion")
            


    def _check_status_api(self):
        if self.api.error :
            self.var = [("error",self.api.error)]
            self.state.popup("error")
        if self.api.code:
            self.var = [("site",self.api.site),("code",self.api.code)]
            self.state.popup("need_auth")
            self.var =[]
        if self.api.auth == True:
            self.state.rm_popup("need_auth")
        if self.api.maintenance == True:
            self.state.popup("maintenance")
        else:
            self.state.rm_popup("maintenance")


    def runtime(self):
        self._check_timer()
        self._check_status_vue()
        self.screen.runtime()
        self._check_connexion_api()
        self._check_status_api()
        self._render()
  
    def is_runnig(self):
        return self.running
    
    def stop(self):
        self.screen.stop()
        self.running = False