import os
import pygame
import argparse
import cv2
import numpy as np
import time
from utils import paragraph, position

pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'

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
        self.normal_font = pygame.font.Font("./font/NittiGrotesk-ExtraBlack.otf", 150)
        self.cta_font = pygame.font.Font("./font/NittiGrotesk-ExtraBlack.otf", 80)
        self.evolution = 0
        self.sequence = []
        self.cam_open = False
        self.camera = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
        self.countdown = False
        self.countdown_time = 5

    def afficher_welcome(self):
        self.fenetre.fill(self.colour_bg)
        text_welcome = paragraph(
            "UNE PETITE PHOTO\nDÉTECTIVE?",
            color = (255,255,255),
            font = self.normal_font,
            align = "center"
            )
        
        text_cta = paragraph(
            "Appuyer sur le pédalier",
            font = self.cta_font,
            align = "center"
        )

        self.fenetre.blit(text_welcome, position(self.fenetre,text_welcome,v_align = "center",h_align="center"))      
        self.fenetre.blit(text_cta, position(self.fenetre,text_cta,v_align = "center",h_align="bottom"))
        pygame.display.flip() 


    def afficher_cgv(self):
        self.fenetre.fill(self.colour_bg)
        text_cgv = paragraph(
            "LA PHOTO VA ETRE\nAJOUTÉE SUR FACEBOOK !\n\nSI VOUS NE LE SOUHAITEZ PAS\nFAITES LA AVEC VOTRE\nTÉLÉPHONE",
            color = (255,255,255),
            font = self.cta_font,
            align = "center"
            )
        
        self.fenetre.blit(text_cgv, position(self.fenetre,text_cgv,v_align = "center",h_align="center"))        
        pygame.display.flip()

    def start_photo(self):
        self.cam_open = True

    def stop_photo(self):
        self.cam_open = False

    def start_countdown(self):
        self.start_ticks=pygame.time.get_ticks()
        self.countdown = True
        
    def stop_countdown(self):
        self.countdown = False

    def next_sequence(self):
        self.evolution = self.evolution + 1
        self.sequence[self.evolution]()

    def relancer(self):
        self.evolution = 0
        self.sequence[self.evolution]()

    def afficher_camera(self,countdown = False):
        self.fenetre.fill(self.colour_bg)
        ret, framecv = self.camera.read()    
        frame = cv2.cvtColor(framecv, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        frame = pygame.surfarray.make_surface(frame)
        self.fenetre.blit(frame, (0,0))
        
        if countdown == False:
            text_info = paragraph(
            "APPUYER SUR LE PEDALIER\n POUR PRENDRE LA PHOTO",
            color = (242, 101, 34),
            font = self.cta_font,
            align = "center"
            )
            self.fenetre.blit(text_info, position(self.fenetre,text_info,v_align = "center",h_align="bottom"))   
            
        else :
            seconds=(pygame.time.get_ticks()-self.start_ticks)/1000 #calculate how many seconds
            if self.countdown_time - seconds > 0.8 : # if more than 10 seconds close the game
                text = str(int(self.countdown_time - seconds))
                if int(self.countdown_time - seconds) <= 1:
                    text = "ATTENTION"
                countdown_text = paragraph(
                    text,
                    color = (242, 101, 34),
                    font = self.normal_font,
                    align = "center"
                )  
                self.fenetre.blit(countdown_text, position(self.fenetre,countdown_text,v_align = "center",h_align="center"))  
            elif self.countdown_time - seconds <= 0.8 and self.countdown_time - seconds > 0 : 
                countdown_text = paragraph(
                    "SOURIEZ",
                    color = (242, 101, 34),
                    font = self.normal_font,
                    align = "center"
                )
            
                self.fenetre.blit(countdown_text, position(self.fenetre,countdown_text,v_align = "center",h_align="center"))  
            else:
                print("prendre la photo")
                self.photo = framecv
                self.stop_countdown()
                self.stop_photo()
                self.next_sequence()
        pygame.display.flip()


    def ajout_du_logo(self):
        watermark = cv2.imread('./logo/logo.png', cv2.IMREAD_UNCHANGED)
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
        print("Resized...")
        self.photo = cv2.addWeighted(self.photo,1,overlay,1,0)
        self.photo = np.flip(self.photo, 1)

    def afficher_rendu_photo(self):
        self.fenetre.fill(self.colour_bg)
        self.ajout_du_logo()
        border = pygame.Surface((960+20, 540+20))
        border.fill(pygame.Color(255,255,255))
        self.fenetre.blit(border, position(self.fenetre,border,v_align = "center",h_align=20))
        frame = cv2.cvtColor(self.photo, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        frame = cv2.resize(frame, dsize=(540,960), interpolation=cv2.INTER_CUBIC)
        frame = pygame.surfarray.make_surface(frame)
        self.fenetre.blit(frame, position(self.fenetre,frame,v_align = "center",h_align=30))
        info_text = paragraph(
            "La photo vous plait ?",
            color = (255, 255, 255),
            font = self.cta_font,
            align = "center"
        )
        self.fenetre.blit(info_text, position(self.fenetre,info_text,v_align = "center",h_align="bottom"))  
        pygame.display.flip()

    def sauver_photo(self):
        timestr = time.strftime("%d-%m-%Y_%H%M%S")
        file = "PHOTO_" + timestr + ".jpg"
        cv2.imwrite(filename='./photo/' + file, img=self.photo)

    def afficher_remerciement(self):
        self.sauver_photo()
        self.fenetre.fill(self.colour_bg)
        info_text = paragraph(
            "MERCI POUR LA PHOTO !\n\nRECUPEREZ LA MARDI\nSUR FACEBOOK\n\nA LA PROCHAINE !",
            color = (255, 255, 255),
            font = self.cta_font,
            align = "center"
        )
        self.fenetre.blit(info_text, position(self.fenetre,info_text,v_align = "center",h_align="center"))  
        pygame.display.flip()
        time.sleep(5)
        self.relancer()

        
    def exit(self):
        print("this is end now")
        self.continuer = False     
        exit()


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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    print("z")
                    self.next_sequence()
                    
 


    def game(self):
        # self.sequence.append(self.afficher_welcome)
        # self.sequence.append(self.afficher_cgv)
        self.sequence.append(self.start_photo)
        self.sequence.append(self.start_countdown)
        self.sequence.append(self.afficher_rendu_photo)
        self.sequence.append(self.afficher_remerciement)
        self.sequence[self.evolution]()
        pygame.display.flip()
        while self.continuer:
            if self.cam_open :
                self.afficher_camera(self.countdown)
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