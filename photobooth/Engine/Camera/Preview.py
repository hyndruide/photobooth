import pygame
import numpy as np
import cv2
from photobooth.Engine.Vue.Fonts import Fonts
from photobooth.Engine.Vue.Vue import Vue
from photobooth.utils_image import ajout_du_logo, save_photo

class Preview(Vue):
    def __init__(self,*args,**kwargs):
        Vue.__init__(self,*args,**kwargs)

    def load_photo(self,photo):
        self.photo = photo
   
    def load_render(self,screen):
        self.screen_name = screen["vue"]
        self.thumbail, self.photo = ajout_du_logo(self.photo)
        self._done = False

    def make_render(self):
        self.parent_surface.fill(self.template.background)

        marge = pygame.Surface(self.template.marge_size)
        marge.fill(pygame.Color(self.template.marge_color))
        self._blit_surface(marge, self.template.marge_pos)

        self._blit_surface(self.thumbail, self.template.photo_pos)
        
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