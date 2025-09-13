from pygame import transform
class Doll:
    def __init__(self, width, height, image):
        self.width = width
        self.height = height
        self.image = image
        self.image = transform.scale(self.image, (self.width, self.height))
        self.is_forward = False