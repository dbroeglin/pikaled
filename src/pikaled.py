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
    def __init__(self, url = None, canvas = None, matrix = None, tachi_size = 9):
        self.url = url
        self.canvas = canvas
        self.matrix = matrix
        self.tachi_size = tachi_size
        
        intermediate_color=(255,255,255)
        final_color=(255,255,255)

        self.miss = self.draw_miss(intermediate_color)
        self.final_miss = self.draw_miss(final_color, background_color=(100,0,0))
        self.hit = self.draw_hit(intermediate_color)
        self.final_hit = self.draw_hit(final_color, background_color=(100,0,0))
        self.unknown = self.draw_unknown(intermediate_color)
        self.blank = self.draw_blank()

    def draw_blank(self):
        blank = Image.new("RGB", (16, 16))
        draw = ImageDraw.Draw(blank)
        draw.rectangle([(0, 0), (15, 15)], fill=(0,0,0), outline=(0,0,0), width=1)
        return blank

    def draw_hit(self, color, background_color=(0,0,0)):
        hit = Image.new("RGB", (16, 16), color=background_color)
        draw = ImageDraw.Draw(hit)
        draw.ellipse([(1,1), (14, 14)], fill=background_color, outline=color, width=3)
        return hit

    def draw_miss(self, color, background_color=(0,0,0)):
        miss = Image.new("RGB", (16, 16), color=background_color)
        draw = ImageDraw.Draw(miss)
        draw.line([(0, 0), (14, 14)], fill=color, width=3)
        draw.line([(0, 15), (15, 0)], fill=color, width=3)
        draw.rectangle([(0, 0), (15, 15)], fill=None, outline=background_color, width=1)
        return miss

    def draw_unknown(self, color):
        font = ImageFont.truetype('Roboto-Black.ttf', 19)
        unknown = Image.new("RGB", (16, 16))
        draw = ImageDraw.Draw(unknown)
        draw.text((8, 8), "?", font=font, anchor="mm", features=["-kern"], color=color)        

    def update(self):
        scoreboard = self.get_scoreboard()
        if scoreboard is None or scoreboard.tachi is None or scoreboard.tachi.participants is None:
            self.blank_scoreboard()
        else:
            for (line_nb, participant) in enumerate(scoreboard.tachi.participants):
                for (index, result) in enumerate(participant.score.results):
                    self.display_result(self.canvas, result, line_nb, index)
            for line_nb in range(len(scoreboard.tachi.participants), self.tachi_size):
                for index in range(4):
                    self.display_result(self.canvas, None, line_nb, index)
        if isinstance(self.canvas, SimulationCanvas):
            self.canvas.update()
        else:
            self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def get_scoreboard(self):
        try:
            response = httpx.get(self.url)
            response.raise_for_status()
            try:
                return Scoreboard.model_validate(response.json())
            except ValidationError as err:
                print(err)
                exit(1)
        except httpx.HTTPError as err:
            print(f"Error fetching scoreboard: {err}")
            return None

    def blank_scoreboard(self):
        for line_nb in range(self.tachi_size):
            for index in range(4):
                self.display_result(self.canvas, None, line_nb, index)

    def get_image(self, result):
        if result.status is None:
            return self.blank
        if result.status == "hit":
            if result.final:
                return self.final_hit
            else:
                return self.hit
        elif result.status == "miss":
            if result.final:
                return self.final_miss
            else:
                return self.miss
        elif result.status == "unknown":
            return self.unknown
        else:
            raise ValueError("Invalid result status: {}".format(status))

    def rotate_image(self, image):
        return ImageOps.flip(ImageOps.mirror(image))

    def display_result(self, canvas, result, participant_nb, arrow_nb):
        if result is None:
            img = self.blank
        else:
            img = self.get_image(result)
        if participant_nb == 0:
            canvas.SetImage(self.rotate_image(img), (3 - arrow_nb) * 16, 32)
        elif participant_nb == 1:
            canvas.SetImage(img,  (4 + arrow_nb) * 16, 32)
        elif participant_nb == 2:
            canvas.SetImage(self.rotate_image(img),  (8 + (3 - arrow_nb)) * 16, 32)
        elif participant_nb == 3:
            canvas.SetImage(self.rotate_image(img),  (8 + (3 - arrow_nb)) * 16, 16)
        elif participant_nb == 4:
            canvas.SetImage(img,  (4 + arrow_nb) * 16, 16)
        elif participant_nb == 5:
            canvas.SetImage(self.rotate_image(img), (3 - arrow_nb) * 16, 16)
        elif participant_nb == 6:
            canvas.SetImage(self.rotate_image(img),  (8 + (3 - arrow_nb)) * 16, 0)
        elif participant_nb == 7:
            canvas.SetImage(img,  (4 + arrow_nb) * 16, 0)
        elif participant_nb == 8:
            canvas.SetImage(self.rotate_image(img), (3 - arrow_nb) * 16, 0)
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
            tuple: The transformed coordinates (new_x, new_y). The new coordinates are 
            transformed to the position on the screen that corresponds to the physical
            layout of the LED matrix.
        """
        if y < 16: # chain 1
            if x < 64:
                return 63 - x, 143 - y
            elif x < 128:
                return x - 64, 112 + y
            elif x < 192:
                return 63 - (x - 128), 111 - y
            else:
                raise ValueError("Invalid x-coordinate: {}".format(x))
        elif y < 32: # chain 2
            if x < 64:
                return 63 - x, 95 - (y - 16)
            elif x < 128:
                return x - 64, 64 + (y - 16)
            elif x < 192:
                return 63 - (x - 128), 63 - (y - 16)
            else:
                raise ValueError("Invalid x-coordinate: {}".format(x))
        elif y < 48: # chain 3  
            if x < 64:
                return 63 - x, 15 - (y - 32)
            elif x < 128:
                return x - 64, 16 + (y - 32)
            elif x < 192:
                return 63 - (x - 128), 47 - (y - 32)
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

