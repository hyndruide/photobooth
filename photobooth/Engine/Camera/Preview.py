import pygame
import numpy as np
import cv2
from photobooth.Engine.Vue.Fonts import Fonts
from photobooth.Engine.Vue.Vue import Vue
from photobooth.utils_image import ajout_du_logo, save_photo

class Preview(Vue):
    def __init__(self,parent_surface,font = Fonts()):
        Vue.__init__(self,parent_surface,font)

    def load_photo(self,photo):
        self.photo = photo
   
    def load_render(self,screen):
        self.screen_name = screen["vue"]
        self.template.load(self.screen_name)
        self.marge_size = (screen["photo_size"][0]+screen["marge"][0],screen["photo_size"][1]+screen["marge"][1])
        self.marge_color = self.template.get_color(screen["marge_color"])
        self.marge_pos = (screen["marge_pos"][0],screen["marge_pos"][1])
        self.photo_size = (screen["photo_size"][0],screen["photo_size"][1])
        self.photo_pos = (screen["photo_pos"][0],screen["photo_pos"][1])
        self.path_logo= screen["logo"]
        self.photo = ajout_du_logo(self.photo,self.path_logo)
        self._done = False

    def make_render(self):
        self.parent_surface.fill(self.template.background)

        marge = pygame.Surface(self.marge_size)
        marge.fill(pygame.Color(self.marge_color))
        self._blit_surface(marge, self.marge_pos)

        frame = cv2.cvtColor(self.photo, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        frame = cv2.resize(frame, dsize=(540,960), interpolation=cv2.INTER_CUBIC)
        frame = pygame.surfarray.make_surface(frame)
        self._blit_surface(frame, self.photo_pos)
        
        self.make_render_text()

    def get_data(self):
        if hasattr(self, 'filename'):
            return self.filename
        else :
            return None

    def next(self):
        self.filename = save_photo(self.photo)
        self._done = True
    
    def prev(self):
        return True