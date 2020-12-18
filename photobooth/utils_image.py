import pkg_resources
import time
import os
import json
import pygame
from PIL import Image

def ajout_du_logo(photo_src):
    if os.path.isfile('./photobooth/json/settings.json'):
        with open('./photobooth/json/settings.json', 'r') as f1:
            data = json.load(f1)
    logo = data['logo']
    strFormat = 'RGBA'
    raw_str = pygame.image.tostring(photo_src, strFormat, False)
    image = Image.frombytes(strFormat, photo_src.get_size(), raw_str)
    logo = pkg_resources.resource_filename("photobooth", logo)
    watermark = Image.open(logo)
    width, height = image.size
    photo = Image.new('RGBA', (width, height), (0,0,0,0))
    photo.paste(image, (0,0))
    wpht,hpht = photo.size
    wlogo,hlogo = watermark.size
    photo.paste(watermark, (10,hpht-hlogo-10), mask=watermark)
    photo_thumbail = photo.resize((960,540), Image.ANTIALIAS)
    raw_str = photo_thumbail.convert(strFormat).tobytes()
    surface = pygame.image.fromstring(raw_str, (960,540), strFormat)
    raw_str = photo.convert(strFormat).tobytes()
    photo = pygame.image.fromstring(raw_str, (width, height), strFormat)


    return surface,photo

def save_photo(photo_src):
    strFormat = 'RGBA'
    raw_str = pygame.image.tostring(photo_src, strFormat, False)
    image = Image.frombytes(strFormat, photo_src.get_size(), raw_str)
    timestr = time.strftime("%d-%m-%Y_%H%M%S")
    file = "PHOTO_" + timestr + ".jpg"
    image.convert("RGB").save('./photo/' + file,"JPEG")
    return file