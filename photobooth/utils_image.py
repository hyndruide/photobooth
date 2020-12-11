import cv2
import numpy as np
import pkg_resources
import time
import os
import json

def ajout_du_logo(photo):
    if os.path.isfile('./photobooth/json/settings.json'):
        with open('./photobooth/json/settings.json', 'r') as f1:
            data = json.load(f1)
    logo = data['logo']
    logo = pkg_resources.resource_filename("photobooth", logo)
    watermark = cv2.imread(logo, cv2.IMREAD_UNCHANGED)
    (wH, wW) = watermark.shape[:2]
    (B, G, R, A) = cv2.split(watermark)
    B = cv2.bitwise_and(B, B, mask=A)
    G = cv2.bitwise_and(G, G, mask=A)
    R = cv2.bitwise_and(R, R, mask=A)
    watermark = cv2.merge([B, G, R, A])
    (h, w) = photo.shape[:2]
    photo = np.dstack([photo, np.ones((h, w), dtype="uint8") * 255])
    overlay = np.zeros((h, w, 4), dtype="uint8")
    overlay[h - wH - 10:h - 10, w - wW - 950:w - 950] = watermark
    photo = cv2.addWeighted(photo,1,overlay,1,0)
    photo = np.flip(photo, 1)
    return photo

def save_photo(photo):
    photo = np.flip(photo, 1)
    timestr = time.strftime("%d-%m-%Y_%H%M%S")
    file = "PHOTO_" + timestr + ".jpg"
    cv2.imwrite(filename='./photo/' + file, img=photo)
    return file