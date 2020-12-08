import os
import pygame
import argparse
import cv2
import numpy as np
import time
import threading
from .utils import paragraph, position
import pkg_resources
from BoothClient.BoothClient import BoothClient

pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'

WHITE = (255, 255, 255)
ORANGE = (242, 101, 34)
RED = (255, 0, 0)
class photobooth:
    """docstring for ClassName"""
    def __init__(self, fullscreen):

        display_flags = 0
        if fullscreen:
            display_flags |= pygame.FULLSCREEN
        self.size_fenetre = (1280, 720)
        self.fenetre = pygame.display.set_mode(self.size_fenetre, display_flags)
        self.continuer = True
        self.colour_bg = [0, 0, 0]
        font_file = pkg_resources.resource_filename("photobooth", "font/NittiGrotesk-ExtraBlack.otf")
        self.normal_font = pygame.font.Font(font_file, 150)
        self.cta_font = pygame.font.Font(font_file, 80)
        self.error_font = pygame.font.Font(font_file, 50)
        self.evolution = 0
        self.sequence = []
        self.cam_open = False
        self.countdown = False
        self.countdown_time = 5
        self.reset_time = 20
        self.api = BoothClient()
        self.ask_connection = False
        self.counter_reset = True

    def blit_window(self, what, v_align, h_align):
        target = self.fenetre
        target.blit(what, position(target, what, v_align, h_align))

    def afficher_erreur(self,value_error):
        self.fenetre.fill(self.colour_bg)
        error = paragraph("il y a un probleme !", self.cta_font, RED, "center")
        error_info = paragraph(str(value_error), self.error_font, RED, "center")
        self.blit_window(error, "center", "top")
        self.blit_window(error_info, "center", "center")
        pygame.display.flip()


    def connect_api(self):
        self.counter_reset = False
        try:
            if self.api.connect() == False:
                try:
                    self.api.first_connect()
                except Exception as error:
                    print(repr(error))
                    self.afficher_erreur(repr(error))
                else :
                    self.ask_connection = True
                    self.afficher_auth_connexion()
                    self.start_ticks_auth = pygame.time.get_ticks()
            else :
                self.validate_connexion()
        except ConnectionError:
            self.afficher_no_connexion()
            del self.sequence[0]
            self.evolution = -1


    def afficher_no_connexion(self):
        self.fenetre.fill(self.colour_bg)
        info = paragraph("Pas de connexion internet\nles photos seront stocké\nelles seront envoyées\nà la prochaine connection", self.cta_font, WHITE, "center")
        self.blit_window(info, "center", "top")
        info = paragraph("appuyer à droite\npour passer", self.error_font, ORANGE, "center")
        self.blit_window(info, "right", "bottom")
        info = paragraph("appuyer à gauche\npour reconnecter", self.error_font, ORANGE, "left")
        self.blit_window(info, "left", "bottom")
        pygame.display.flip()

    def afficher_auth_connexion(self):
        self.fenetre.fill(self.colour_bg)
        info = paragraph("premiere connnexion !\nVeuillez vous rendre sur le site\nhttp:\\\\superphoto.fr\npour ajouter votre photobooth\navec le code : ", self.cta_font, WHITE, "center")
        self.blit_window(info, "center", "top")
        info = paragraph(self.api.req['user_code'], self.normal_font, ORANGE, "center")
        self.blit_window(info, "center", 400)
        pygame.display.flip()

    def validate_connexion(self):
        self.ask_connection = False
        del self.sequence[0]
        self.sequence[self.evolution]()
        self.restart_counter_reset()
        self.counter_reset = True          

    def afficher_welcome(self):
        self.counter_reset = True
        self.fenetre.fill(self.colour_bg)

        welcome = paragraph("UNE PETITE PHOTO\nDÉTECTIVE?", self.normal_font, WHITE, "center")
        self.blit_window(welcome, "center", "center")

        cta = paragraph("Appuyer sur le pédalier", self.cta_font, WHITE, "center")
        self.blit_window(cta, "center", "bottom")

        pygame.display.flip()

    def afficher_cgv(self):
        self.fenetre.fill(self.colour_bg)

        text = "LA PHOTO VA ETRE\nAJOUTÉE SUR FACEBOOK !\n\nSI VOUS NE LE SOUHAITEZ PAS\nFAITES LA AVEC VOTRE\nTÉLÉPHONE"
        cgv = paragraph(text, self.cta_font, WHITE, "center")
        self.blit_window(cgv, "center", "center")

        pygame.display.flip()

    def start_photo(self):
        self.camera = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
        self.cam_open = True

    def stop_photo(self):
        
        self.camera.release()
        self.cam_open = False

    def start_countdown(self):
        self.start_ticks=pygame.time.get_ticks()
        self.countdown = True
        
    def stop_countdown(self):
        self.countdown = False

    def next_sequence(self):
        self.evolution = self.evolution + 1
        self.sequence[self.evolution]()
        print(self.sequence[self.evolution].__func__.__name__)

    def prev_sequence(self,step = 1):
        self.evolution = self.evolution - step
        self.sequence[self.evolution]()
        print(self.sequence[self.evolution].__func__.__name__)

    def relancer_sequence(self):
        self.start_ticks_reset=pygame.time.get_ticks()
        self.evolution = 0
        self.sequence[self.evolution]()
        print(self.sequence[self.evolution].__func__.__name__)

    def afficher_camera(self):
        self.fenetre.fill(self.colour_bg)
        ret, framecv = self.camera.read()    
        frame = cv2.cvtColor(framecv, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        frame = pygame.surfarray.make_surface(frame)
        self.fenetre.blit(frame, (0,0))
        
        if self.countdown == False:
            text = "APPUYER SUR LE PEDALIER\n POUR PRENDRE LA PHOTO"
            info = paragraph(text, self.cta_font, ORANGE, "center")
            self.blit_window(info, "center", "bottom")

        else :
            seconds=(pygame.time.get_ticks()-self.start_ticks)/1000 #calculate how many seconds

            time_left = self.countdown_time - seconds

            # TODO: on peut simplifier ce code
            if time_left > 0.8:
                if time_left <= 1:
                    text = "ATTENTION"
                else:
                    text = str(int(time_left))

                p = paragraph(text, self.normal_font, ORANGE, "center")
                self.blit_window(p, "center", "center")

            elif time_left <= 0.8 and time_left > 0 :
                text = "SOURIEZ"
                p = paragraph(text, self.normal_font, ORANGE, "center")
                self.blit_window(p, "center", "center")

            else:
                print("prendre la photo")
                self.photo = framecv
                self.stop_countdown()
                self.stop_photo()
                self.restart_counter_reset()
                self.next_sequence()
        pygame.display.flip()


    def ajout_du_logo(self):
        logo = pkg_resources.resource_filename("photobooth", "logo/logo.png")
        watermark = cv2.imread(logo, cv2.IMREAD_UNCHANGED)
        (wH, wW) = watermark.shape[:2]
        (B, G, R, A) = cv2.split(watermark)
        B = cv2.bitwise_and(B, B, mask=A)
        G = cv2.bitwise_and(G, G, mask=A)
        R = cv2.bitwise_and(R, R, mask=A)
        watermark = cv2.merge([B, G, R, A])
        (h, w) = self.photo.shape[:2]
        self.photo = np.dstack([self.photo, np.ones((h, w), dtype="uint8") * 255])
        overlay = np.zeros((h, w, 4), dtype="uint8")
        overlay[h - wH - 10:h - 10, w - wW - 950:w - 950] = watermark
        self.photo = cv2.addWeighted(self.photo,1,overlay,1,0)
        self.photo = np.flip(self.photo, 1)

    def afficher_rendu_photo(self):
        self.fenetre.fill(self.colour_bg)
        self.ajout_du_logo()
        border = pygame.Surface((960+20, 540+20))
        border.fill(pygame.Color(255,255,255))
        self.blit_window(border, "center", 20)

        frame = cv2.cvtColor(self.photo, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        frame = cv2.resize(frame, dsize=(540,960), interpolation=cv2.INTER_CUBIC)
        frame = pygame.surfarray.make_surface(frame)
        self.blit_window(frame, "center", 30)

        text = "La photo vous plait ?"
        info = paragraph(text, self.cta_font, WHITE, "center")
        self.blit_window(info, "center", "bottom")

        pygame.display.flip()

    def restart_counter_reset(self):
        self.start_ticks_reset=pygame.time.get_ticks()

    def sauver_photo(self):
        timestr = time.strftime("%d-%m-%Y_%H%M%S")
        file = "PHOTO_" + timestr + ".jpg"
        cv2.imwrite(filename='./photo/' + file, img=self.photo)
        return file

    def send_photo(self,filename):
        reponse = self.api.upload("./photo/"+filename)
        if 'id' in reponse:
            os.remove("./photo/"+filename)

    def afficher_remerciement(self):
        self.fenetre.fill(self.colour_bg)
        text = "MERCI POUR LA PHOTO !\n\nRECUPEREZ LA MARDI\nSUR FACEBOOK\n\nA LA PROCHAINE !"
        info = paragraph(text, self.cta_font, WHITE, "center")
        self.blit_window(info, "center", "center")

        pygame.display.flip()
        filename = self.sauver_photo()
        self.send_photo(filename)
        time.sleep(5)
        self.relancer_sequence()

        
    def exit(self):
        print("this is end now")
        self.continuer = False     
        exit()

    def upload_photos(self):
        listeFichiers = []
        for (rep, sousRep, fichiers) in os.walk("./photo/"):
            listeFichiers.extend(fichiers)
        for filename in listeFichiers:
            self.send_photo(filename)


    def event(self):
        for event in self.events:  
            if event.type == pygame.QUIT:
                self.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    print("a")
                    if self.sequence[self.evolution].__func__.__name__ == "afficher_rendu_photo":
                        self.prev_sequence(2)
                        self.next_sequence()
                    else :
                        if self.cam_open:
                            self.stop_photo()
                            self.stop_countdown()
                        self.relancer_sequence()
                        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    print("z")
                    self.next_sequence()
                    
    def load_sequence(self):
        self.sequence.append(self.connect_api)
        self.sequence.append(self.afficher_welcome)
        self.sequence.append(self.afficher_cgv)
        self.sequence.append(self.start_photo)
        self.sequence.append(self.start_countdown)
        self.sequence.append(self.afficher_rendu_photo)
        self.sequence.append(self.afficher_remerciement)


    def game(self):
        self.load_sequence()
        self.relancer_sequence()
        self.upload_photos()
        while self.continuer:
            seconds=(pygame.time.get_ticks()-self.start_ticks_reset)/1000 
            time_left_reset = self.reset_time - seconds
            if self.ask_connection :
                seconds=(pygame.time.get_ticks()-self.start_ticks_auth)/1000 #calculate how many seconds
                time_left_auth = self.api.req['interval'] - seconds
                if time_left_auth < 0:
                    if self.api.ask_first_connect() == False:
                        self.validate_connexion()

                    self.start_ticks_auth = pygame.time.get_ticks()
                    self.restart_counter_reset()
            if time_left_reset <0 and not self.cam_open and self.counter_reset :
                print("reset")
                self.relancer_sequence()
                self.upload_photos()
            if self.cam_open :
                self.afficher_camera()

            self.events = pygame.event.get()
            self.event()

def main():
	parser = argparse.ArgumentParser()
	# parser.add_argument("-s", "--serial", default="/dev/ttyUSB0")
	# parser.add_argument("--serial-baud", default=115200, type=int)
	parser.add_argument("--window", help="Start in window mode (no fullscreen)",
		action="store_false", default=True, dest="fullscreen")
	args = parser.parse_args()

	# arduino = utils.Arduino(args.serial, args.serial_baud)
	# webcam = utils.Webcam()

	jeu = photobooth(args.fullscreen)
	jeu.game()


if __name__ == '__main__':
	main()