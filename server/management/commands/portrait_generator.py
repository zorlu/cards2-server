from django.core.management.base import BaseCommand
import os
import time
import numpy
from PIL import Image
from app.fractal import Fractal
from app import settings

class Command(BaseCommand):
    def handle(self, *args, **options):

        # Random fractal curve
        # FB - 201107096
        import math
        import random
        imgx = 300
        imgy = 600
        image = Image.new("RGB", (imgx, imgy))
        c = random.random()

        def frCurve(xa, ya, xb, yb):
            xa = int(xa)
            xb = int(xb)
            ya = int(ya)
            yb = int(yb)
            dx = xb - xa
            dy = yb - ya
            d = math.hypot(dx, dy)
            if d <= 1:
                if xa >= 0 and xa < imgx and ya >= 0 and ya < imgy:
                    image.putpixel((xa, ya), (0, 255, 0))
                if xb >= 0 and xb < imgx and yb >= 0 and yb < imgy:
                    image.putpixel((xb, yb), (0, 255, 0))
                return
            xm = xa + dx * c
            ym = ya + dy * c + math.copysign(dx * c, random.random() - 0.5)
            frCurve(xa, ya, xm, ym)
            frCurve(xm, ym, xb, yb)

        # main
        frCurve(0, (imgy - 1) / 2, imgx - 1, (imgy - 1) / 2)
        image.save("Random_Fractal_Curve.png", "PNG")
