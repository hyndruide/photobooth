from photobooth.Engine.Vue.Template import Template
from photobooth.Engine.Vue.Fonts import Fonts
from photobooth.utils import make_paragraphe, position

class Vue:
    ''' Class permetant d'afficher les Vue dans l'engine '''
    def __init__(self, parent_surface, template ,font):
        self.template = template
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


    def make_render_text(self):
        ''' cree les ligne de texte grace aux template'''
        generateur_paragraphe = self.template.gen_para(self.var)
        for paragraphe in generateur_paragraphe:
            vue_paragraphe = make_paragraphe(
                paragraphe["text"],
                self.font.get_font(paragraphe['size']),
                paragraphe['color'],
                paragraphe['align']
            )
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

    def runtime(self):
        pass

    




        



