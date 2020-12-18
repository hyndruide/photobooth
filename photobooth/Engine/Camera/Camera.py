import pygame
import pygame.camera
from photobooth.Engine.Vue.Fonts import Fonts
from photobooth.Engine.Vue.Vue import Vue

class Camera(Vue):
    def __init__(self,*args,**kwargs):
        Vue.__init__(self,*args,**kwargs)
        pygame.camera.init()
        self.tick =0
        self._start_timer = False

    def set_timer(self,timer=5):
        self.timer = timer
 
    def start_timer(self):
        self.tick = pygame.time.get_ticks()
        self._start_timer = True

    def runtime(self):
        if self._start_timer == True:
            seconds=(pygame.time.get_ticks()-self.tick)/1000
            self.time_left = self.timer - seconds
            if self.time_left < 0:
                self.take_photo()
                self._start_timer = False
                self.next()  
                
            elif self.time_left <= 0.8 and self.time_left > 0:
                self.countdown ="SOURIEZ"
            elif self.time_left <= 1.5:
                self.countdown ="ATTENTION"
            else:
                self.countdown = str(int(self.time_left))

    def take_photo(self):
        self.photo = self.camera.get_image()


    def load_render(self,screen):
        if not self.camera.query_image():
            print('yop')
            self.camera.start()
            self.camera.set_controls(hflip = True, vflip = False)
        self.screen_name = screen["vue"]
        if self.screen_name == "camera_timer":
            self.set_timer(screen["timer"])
            self.start_timer()
        self._done = False

    def make_render(self):
        if self.camera.query_image():
            frame = self.camera.get_image()
            self.parent_surface.blit(frame, (0,0))
            if self.screen_name == "camera_timer":
                self.var = [("timer",self.countdown)]
                self.make_render_text()
            else:
                self.make_render_text()

    def get_data(self):
        if hasattr(self, 'photo'):
            return self.photo
        else :
            return None

    def stop(self):
        self.camera.stop()
