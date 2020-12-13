import pygame 
import json
import pkg_resources
import os


class Fonts:
    def __init__(self):
        pygame.init()
        self._load_json()
        

    def _load_json(self):
        self.typo = {}
        path = "photobooth/json/font.json"
        if os.path.isfile(path):
            with open(path,'r') as file:
                data = json.load(file)
        else:
            print("lost")
        police = data['font']
        font_size = data['font_size']
        font_file = pkg_resources.resource_filename(
            "photobooth",
            "font/" + police
            )
        for key, value in font_size.items():
            self.typo[key] = pygame.font.Font(font_file, value)
        
    def get_font(self,size):
        return self.typo[size]