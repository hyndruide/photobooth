import cv2
from .Capture import VideoCaptureThreading
import numpy as np
import pygame
from photobooth.Engine.Vue.Fonts import Fonts
from photobooth.Engine.Vue.Vue import Vue

class Camera(Vue):
    def __init__(self,parent_surface,font = Fonts()):
        Vue.__init__(self,parent_surface,font)
        self.tick =0
        self._start_timer = False
        self.camera = VideoCaptureThreading(0,1280,720)

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
                self.stop_camera() 
                self.next()  
                
            elif self.time_left <= 0.8 and self.time_left > 0:
                self.countdown ="SOURIEZ"
            elif self.time_left <= 1.5:
                self.countdown ="ATTENTION"
            else:
                self.countdown = str(int(self.time_left))

    def take_photo(self):
        self.photo = self.framecv

    def stop_camera(self):
        self.camera.stop()

    def load_render(self,screen):
        self.screen_name = screen["vue"]
        self.camera.start()
        if self.screen_name == "camera_timer":
            self.set_timer(screen["timer"])
            self.start_timer()
        self.template.load(self.screen_name)
        self._done = False

    def make_render(self):
        if self.camera.started:
            self.template.load(self.screen_name)
            _, self.framecv = self.camera.read()    
            frame = cv2.cvtColor(self.framecv, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = pygame.surfarray.make_surface(frame)
            self.parent_surface.blit(frame, (0,0))
            if self.screen_name == "camera_timer":
                self.make_render_text([("timer",self.countdown)])
            else:
                self.make_render_text()

    def get_data(self):
        if hasattr(self, 'photo'):
            return self.photo
        else :
            return None

    def stop(self):
        self.camera.stop()
