import pygame
import json
from photobooth.Engine.Vue.Vue import Vue
from photobooth.Engine.Camera.Camera import Camera
from photobooth.Engine.Camera.Preview import Preview
from BoothClient.Api_Thread import Api_tread
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
        self.surface = surface
        self.running = True
        self._load_engine_file()
        self._need_update = False
        self.client = Api_tread()
        self.vue = Vue(self.surface)
        self.camera = Camera(self.surface)
        self.preview = Preview(self.surface)
        self.client.start()
        self.var = None
        self.state = 0

        

    def _load_engine_file(self):
        with open('photobooth/json/sequence.json', 'r',encoding='utf-8') as file:
            self.data = json.load(file)
        self.sequence = self.data['sequence']
        self.sequence_api = self.data['api']
        
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        if self._state <= 0:
            self._state = 0
        if self._state >= len(self.sequence)-1:
            self._state = len(self.sequence)-1
        self._prerender()

    def _prerender(self,sequence = None):
        if sequence == None:
            sequence = self.sequence[self.state]
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
            self.screen = self.vue
            self.screen.set_var(self.var)
            self.var = None
        elif self.type == "camera":
            self.screen = self.camera
        elif self.type == "preview":
            self.screen = self.preview
            self.screen.load_photo(self.screen_data)
        self.screen.load_render(self.screen_sequence)
        self._need_update = True

    def _render(self):
        if self._need_update or self.always_update:
            self.screen.make_render()
            pygame.display.flip()
            self._need_update = False

    def _restart(self):
        self._launch_timer()
        self.state = 0

    def _launch_timer(self):
        self.tick = pygame.time.get_ticks()

    def _check_status_vue(self):
        if self.screen.is_done() :
            self.screen_data = self.screen.get_data()
            if type(self.screen_data) == str:
                 self.client.send_photo(self.screen_data)
            self.state = self.state + 1

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
             self.state = self.state - 1

    def _check_status_client(self):
        if self.client.flag_error():
            self.var = [("error",str(self.client.get_error()))]
            self._prerender(self.sequence_api[0])
        if self.client.flag_auth():
            self.var = [("site",self.client.get_site()),("code",self.client.get_user_code())]
            self._prerender(self.sequence_api[2])
        if self.client.flag_connect():
            self.client.shut_flag_connect()
            self._restart()

    def runtime(self):
        self._check_timer()
        self._check_status_vue()
        self.camera.runtime()
        self._check_status_client()
        self._render()
  
    def is_runnig(self):
        return self.running
    
    def stop(self):
        self.screen.stop()
        self.running = False


