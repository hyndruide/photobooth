import json
import os

class Template:
    """ charge les template """
    def __init__(self):
        self.colors_panel = self._get_colors_panel()
        self.template_data  = self._load_template_file()
        
    def _load_template_file(self):
        if os.path.isfile('photobooth/json/template.json'):
            with open('photobooth/json/template.json', 'r',encoding='utf-8') as file:
                data = json.load(file)
            return data

    def _get_colors_panel(self):
        if os.path.isfile('photobooth/json/font.json'):
            with open('photobooth/json/font.json','r') as file:
                data = json.load(file)
            return data['colors']

    def get_color(self,color):
        if color not in self.colors_panel:
            return color
        return (self.colors_panel[color][0],self.colors_panel[color][1],self.colors_panel[color][2])

    def _get_background_color(self):
        background = "BLACK"
        if "bg" and "marge" in self.template_vue:
            background = self.template_vue['bg']
        return self.colors_panel[background]

    def load(self,data):
        self.template_vue = self.template_data[data]
        self.background = self._get_background_color()
        self.paragraphe = ''
        if "paragraphe" in self.template_vue:
            self.paragraphe = self.template_vue['paragraphe']
        if "photo_size" and "marge" in self.template_vue:
            self.marge_size = (self.template_vue["photo_size"][0]+self.template_vue["marge"][0],self.template_vue["photo_size"][1]+self.template_vue["marge"][1])
            self.photo_size = (self.template_vue["photo_size"][0],self.template_vue["photo_size"][1])
        if "marge_color" in self.template_vue:           
            self.marge_color = self.get_color(self.template_vue["marge_color"])
        if "marge_pos" in self.template_vue:
            self.marge_pos = (self.template_vue["marge_pos"][0],self.template_vue["marge_pos"][1])
        if "photo_pos" in self.template_vue:
            self.photo_pos = (self.template_vue["photo_pos"][0],self.template_vue["photo_pos"][1])

    def gen_para(self):
        value = {}
        for para in self.paragraphe:
            value['text'] = para['text']
            value['size'] = para['size']
            value['color'] =  self.get_color(para['color'])
            value['align'] =  para['align']
            value['pos'] =  (para['position'][0],para['position'][1])
            yield value


            
        






        
        