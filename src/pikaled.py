import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

class PikaLed:
    def __init__(self):
        font_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Roboto-Black.ttf")
        font = ImageFont.truetype(font_filename, 19)

        black=(0,0,0)
        gray=(100,100,100)
        white=(255,255,255)

        self.hit = Image.new("RGB", (16, 16))
        draw = ImageDraw.Draw(self.hit)
        draw.ellipse([(1,1), (14, 14)], fill=(0,0,0), outline=white, width=3)

        self.miss = Image.new("RGB", (16, 16))  # Can be larger than matrix if wanted!!
        draw = ImageDraw.Draw(self.miss)  # Declare Draw instance before prims
        draw.line([(0, 0), (14, 14)], fill=white, width=3)
        draw.line([(0, 15), (15, 0)], fill=white, width=3)
        draw.rectangle([(0, 0), (15, 15)], fill=None, outline=black, width=1)

        self.unknown = Image.new("RGB", (16, 16))  # Can be larger than matrix if wanted!!
        draw = ImageDraw.Draw(self.unknown)  # Declare Draw instance before prims
        draw.text((8, 8), "?", font=font, anchor="mm", features=["-kern"])

    def get_image(self, result):
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
