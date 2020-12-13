import json
import os
from photobooth.Engine.Vue import colors
import re

class Templates_Collection:
    """ charge les template """
    def __init__(self):
        self.template_data  = self._load_template_file()
        
    def _load_template_file(self):
        if os.path.isfile('photobooth/json/template.json'):
            with open('photobooth/json/template.json', 'r',encoding='utf-8') as file:
                data = json.load(file)
            return data

    def load(self, template_name):
        # faire des trucs
        template_vue = self.template_data[template_name]

        # TODO: abstraction
        if "photo_size" in template_vue:
            template = PreviewTemplate(template_vue)
        else:
            template = Template(template_vue)
        return template


DEFAULT_TEMPLATE = {
    "bg": "BLACK",
    "paragraphe": []
}

class Template:
    def __init__(self, conf):
        t = {}
        t.update(**DEFAULT_TEMPLATE)
        t.update(**conf)

        self.background = colors.get(t['bg'])
        self.paragraphe = t['paragraphe']

    def gen_para(self, var):
        value = {}
        for para in self.paragraphe:
            value['text'] = replace(para['text'], var)
            value['size'] = para['size']
            value['color'] = colors.get(para['color'])
            value['align'] = para['align']
            value['pos'] =  (para['position'][0],para['position'][1])
            yield value


def replace(phrase, variable_tab):
    if variable_tab is None:
        variable_tab = []

    for variable in variable_tab:
        var,text = variable
        regex = re.search(r"{{(.*)}}",phrase)
        if bool(regex) and var == regex.group(1):
            phrase = phrase.replace(regex.group(0), text)
    return phrase


class PreviewTemplate(Template):
    def __init__(self, conf):
        super().__init__(conf)

        size = tuple(conf["photo_size"])
        marge = tuple(conf["marge"])

        self.photo_size = size
        self.marge_size = (size[0] + marge[0], size[1] + marge[1])
        self.marge_color = colors.get(conf["marge_color"])
        self.marge_pos = tuple(conf["marge_pos"])
        self.photo_pos = tuple(conf["photo_pos"])