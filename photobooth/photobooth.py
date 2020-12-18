import pygame
import argparse
from photobooth.Engine.Engine import Engine

def main():
    parser = argparse.ArgumentParser()
    # parser.add_argument("-s", "--serial", default="/dev/ttyUSB0")
    # parser.add_argument("--serial-baud", default=115200, type=int)
    parser.add_argument("--window", help="Start in window mode (no fullscreen)", action="store_false", default=True,dest="fullscreen")
    args = parser.parse_args()

    pygame.init()
    pygame.mixer.quit()
    pygame.camera.init()
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)
    display_flags = 0
    if args.fullscreen:
        display_flags |= pygame.FULLSCREEN
    size_fenetre = (1280, 720)
    fenetre = pygame.display.set_mode(size_fenetre,display_flags)
    engine = Engine(fenetre)
    while engine.is_runnig():
        engine.runtime()

        fps = str(int(clock.get_fps()))
        fps_text = font.render(fps, 1, pygame.Color("white"))
        fenetre.blit(fps_text, (10,0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                engine.stop()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    engine.stop()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    engine.prev()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    engine.next()
        
        pygame.display.flip()
        clock.tick(30)
if __name__ == '__main__':
    main()
