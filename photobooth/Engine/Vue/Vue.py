from photobooth.Engine.Vue.Template import Template
from photobooth.Engine.Vue.Fonts import Fonts
from photobooth.utils import make_paragraphe, position
import re

class Vue:
    ''' Class permetant d'afficher les Vue dans l'engine '''
    def __init__(self, parent_surface,font = Fonts()):
        self.template = Template()
        self.parent_surface = parent_surface
        self.font = font
        self._done = False
        self.var=None
        self.freeze = False

    def _blit_surface(self,what, pos):
        v_align, h_align = pos
        target = self.parent_surface
        target.blit(what, position(target, what, v_align, h_align))

    def set_var(self,var):
        ''' Recupere les variable ajouter dans le text

        Parameters:
        var (array): un array de tuple [(nom de la variable, contenu),...]

        '''
        
        self.var = var

    def replace(self,phrase,variable_tab):
        for variable in variable_tab:
            var,text = variable
            regex = re.search(r"{{(.*)}}",phrase)
            if bool(regex) and var == regex.group(1):
                phrase = phrase.replace(regex.group(0), text)
        return phrase

                
    def load_var(self,phrase):
        if self.var !=None:
            return self.replace(phrase,self.var)
        else :
            return phrase

    def make_render_text(self):
        ''' cree les ligne de texte grace aux template'''
        generateur_paragraphe = self.template.gen_para()
        for paragraphe in generateur_paragraphe:
            phrase = self.load_var(paragraphe['text'])
            vue_paragraphe = make_paragraphe(phrase, self.font.get_font(paragraphe['size']), paragraphe['color'], paragraphe['align'])
            self._blit_surface(vue_paragraphe,paragraphe['pos'] )

    def make_render(self):
        self.parent_surface.fill(self.template.background)
        self.make_render_text()

    def is_done(self):
        return self._done

    def load_render(self,screen):
        self.screen_name = screen["vue"]
        self.freeze = False
        if "freeze" in screen:
            self.freeze = screen["freeze"]
        self.template.load(self.screen_name)
        self._done = False

    def next(self):
        if not self.freeze :
            self._done = True


    def prev(self):
        return False

    def get_data(self):
        return None
    
    def stop(self):
        pass

    




        



