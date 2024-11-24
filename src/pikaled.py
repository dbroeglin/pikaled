import os
import sys
import pygame
from PIL import Image, ImageDraw, ImageFont, ImageOps

from pydantic import BaseModel, ValidationError
import httpx

class Taikai(BaseModel):
    name: str

class Result(BaseModel):
    status: str | None = None
    value: int | None = None
    final: bool    

class Score(BaseModel):
    results: list[Result]

class Participant(BaseModel):
    name: str
    score: Score

class Tachi(BaseModel):
    index: int
    round: int
    participants: list[Participant]

class Scoreboard(BaseModel):
    taikai: Taikai
    tachi: Tachi | None = None

class PikaLed:
    def __init__(self, url = None, canvas = None):
        self.url = url
        self.canvas = canvas

        font_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Roboto-Black.ttf")
        font = ImageFont.truetype(font_filename, 19)

        black=(0,0,0)
        gray=(100,100,100)
        white=(255,255,255)

        self.hit = Image.new("RGB", (16, 16))
        draw = ImageDraw.Draw(self.hit)
        draw.ellipse([(1,1), (14, 14)], fill=(0,0,0), outline=white, width=3)

        self.miss = Image.new("RGB", (16, 16))
        draw = ImageDraw.Draw(self.miss)
        draw.line([(0, 0), (14, 14)], fill=white, width=3)
        draw.line([(0, 15), (15, 0)], fill=white, width=3)
        draw.rectangle([(0, 0), (15, 15)], fill=None, outline=black, width=1)

        self.unknown = Image.new("RGB", (16, 16))
        draw = ImageDraw.Draw(self.unknown)
        draw.text((8, 8), "?", font=font, anchor="mm", features=["-kern"])

        self.blank = Image.new("RGB", (16, 16))
        draw = ImageDraw.Draw(self.blank)
        draw.rectangle([(0, 0), (15, 15)], fill=black, outline=black, width=1)

    def update(self):
        scoreboard = self.get_scoreboard()
        if scoreboard.tachi is None or scoreboard.tachi.participants is None:
            self.blank_scoreboard()
        else:
            for (line_nb, participant) in enumerate(scoreboard.tachi.participants):
                for (index, result) in enumerate(participant.score.results):
                    self.display_result(self.canvas, result.status, line_nb, index) 
        self.canvas.update()        

    def get_scoreboard(self):
            response = httpx.get(self.url)
            response.raise_for_status()
            try:
                return Scoreboard.model_validate(response.json())
            except ValidationError as err:
                print(err)
                exit(1)

    def blank_scoreboard(self):
        for line_nb in range(9):
            for index in range(4):
                self.display_result(self.canvas, None, line_nb, index)

    def get_image(self, result):
        if result is None:
            return self.blank
        if result == "hit":
            return self.hit
        elif result == "miss":
            return self.miss
        elif result == "unknown":
            return self.unknown
        else:
            raise ValueError("Invalid result: {}".format(result))

    def rotate_image(self, image):
        return ImageOps.flip(ImageOps.mirror(image))

    def display_result(self, canvas, result, participant_nb, arrow_nb):
        print("Participant {} arrow {} result: {}".format(participant_nb, arrow_nb, result))
        img = self.get_image(result)
        if participant_nb == 0:
            canvas.SetImage(self.rotate_image(img),  (8 + (3 - arrow_nb)) * 16, 0)
        elif participant_nb == 1:
            canvas.SetImage(img,  (4 + arrow_nb) * 16, 0)
        elif participant_nb == 2:
            canvas.SetImage(self.rotate_image(img), (3 - arrow_nb) * 16, 0)
        elif participant_nb == 3:
            canvas.SetImage(self.rotate_image(img), (3 - arrow_nb) * 16, 16)
        elif participant_nb == 4:
            canvas.SetImage(img,  (4 + arrow_nb) * 16, 16)
        elif participant_nb == 5:
            canvas.SetImage(self.rotate_image(img),  (8 + (3 - arrow_nb)) * 16, 16)
        elif participant_nb == 6:
            canvas.SetImage(self.rotate_image(img), (3 - arrow_nb) * 16, 32)
        elif participant_nb == 7:
            canvas.SetImage(img,  (4 + arrow_nb) * 16, 32)
        elif participant_nb == 8:
            canvas.SetImage(self.rotate_image(img),  (8 + (3 - arrow_nb)) * 16, 32)
        else:            
            raise ValueError("Invalid participant number: {}".format(participant_nb))
        

class SimulationCanvas:
    def __init__(self):
        self.grid_width, self.grid_height = 2 * 32, 9 * 16
        self.led_width, self.led_height = 5, 5
        self.screen_width, self.screen_height = self.grid_width * self.led_width, self.grid_height * self.led_height
        self.border_size = 2

        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

    def transform(self, x, y):
        """
        Transforms the coordinates (x, y) to simulate the LED matrix physical layout.

        Args:
            x (int): The x-coordinate to transform.
            y (int): The y-coordinate to transform.

        Returns:
            tuple: The transformed coordinates (new_x, new_y).
        """
        if y < 16:
            if x < 64:
                return 63 - x, 47 - y
            elif x < 128:
                return x - 64, 16 + y
            elif x < 192:
                return 63 - (x - 128), 15 - y
            else:
                raise ValueError("Invalid x-coordinate: {}".format(x))
        elif y < 32:
            if x < 64:
                return 63 - x, 63 - (y - 16)
            elif x < 128:
                return x - 64, 64 + (y - 16)
            elif x < 192:
                return 63 - (x - 128), 95 - (y - 16)
            else:
                raise ValueError("Invalid x-coordinate: {}".format(x))
        elif y < 48:
            if x < 64:
                return 63 - x, 111 - (y - 32)
            elif x < 128:
                return x - 64, 112 + (y - 32)
            elif x < 192:
                return 63 - (x - 128), 143 - (y - 32)
            else:
                raise ValueError("Invalid x-coordinate: {}".format(x))
        else:
            raise ValueError("Invalid y-coordinate: {}".format(y))
    
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

