    
import sys
import time
import pygame

from pikaled import PikaLed

class SimulationCanvas:
    def __init__(self):
        self.grid_width, self.grid_height = 2 * 32, 9 * 16
        self.led_width, self.led_height = 5, 5
        self.screen_width, self.screen_height = self.grid_width * self.led_width, self.grid_height * self.led_height
        self.border_size = 2

        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

    def transform(self, x, y):
        if y < 16:
            if x < 64:
                return 63 - x, 47 - y
            elif x < 128:
                return x - 64, 16 + y
            elif x < 192:
                return 63 - (x - 128), 15 - y
        elif y < 32:
            if x < 64:
                return 63 - x, 63 - (y - 16)
            elif x < 128:
                return x - 64, 63 + (y - 16)
            elif x < 192:
                return 63 - (x - 128), 95 - (y - 16)
        elif y < 48:
            if x < 64:
                return 63 - x, 111 - (y - 32)
            elif x < 128:
                return x - 64, 112 + (y - 32)
            elif x < 192:
                return 63 - (x - 128), 143 - (y - 32)
        else:
            return x, y
    
    def SetImage(self, image, x, y): 
        for ix in range(image.width):
            for iy in range(image.height):
                nx, ny = self.transform(x + ix, y + iy)
                pygame.draw.rect(
                    self.screen,
                    image.getpixel((ix, iy)),
                    (
                        nx * self.led_width,
                        ny * self.led_height,
                        self.led_width - self.border_size,
                        self.led_height - self.border_size,
                    ),
                )

    def update(self):
        pygame.display.flip()

def main():
    canvas = SimulationCanvas()
    pikaled = PikaLed()

    for p in range(9):
        pikaled.display_result(canvas, "hit", p, 0)
        pikaled.display_result(canvas, "miss", p, 1)
        pikaled.display_result(canvas, "unknown", p, 2)
        pikaled.display_result(canvas, "hit", p, 3)
    canvas.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
        time.sleep(0.2)

if __name__ == "__main__":
    main()