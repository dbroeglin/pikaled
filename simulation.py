    
import sys
import time
import pygame

from pikaled import PikaLed
from pikaled import SimulationCanvas



def main():
    pikaled = PikaLed(url='http://localhost:3000/scoreboard/dummy.json', canvas=SimulationCanvas())



    while True:
        pikaled.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
        time.sleep(1)




if __name__ == "__main__":
    main()