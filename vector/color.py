# collect from pygame
from numpy import random, array

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (255, 127, 39)
YELLOW = (255, 201, 14)
RED = (255, 0, 0)
GRAY = (99, 116, 133)

# _gen_colors = {
#     'aliceblue': (240, 248, 255), 'aquamarine': (127, 255, 212), 'azure': (240, 255, 255),
#     'beige': (245, 245, 220), 'bisque': (255, 228, 196),
#     'blanchedalmond': (255, 235, 205), 'blue': (0, 0, 255), 'blueviolet': (138, 43, 226),
#     'brown': (165, 42, 42), 'brown1': (255, 64, 64), 'burlywood': (222, 184, 135),
#     'cadetblue': (95, 158, 160), 'chartreuse': (127, 255, 0), 'chocolate': (210, 105, 30),
#     'gold': (255, 215, 0), 'goldenrod': (218, 165, 32), 'green': (0, 255, 0),
#     'greenyellow': (173, 255, 47), 'honeydew': (240, 255, 240), 'hotpink': (255, 105, 180),
#     'indianred': (205, 92, 92), 'indigo': (75, 0, 130), 'ivory': (255, 255, 240),
#     'lightskyblue': (135, 206, 250), 'lightskyblue1': (176, 226, 255), 'lightslateblue': (132, 112, 255),
#     'lightslategray': (119, 136, 153), 'lightsteelblue': (176, 196, 222),
#     'lightsteelblue1': (202, 225, 255), 'lightyellow': (255, 255, 224), 'limegreen': (50, 205, 50),
#     'linen': (250, 240, 230), 'maroon': (176, 48, 96), 'mediumorchid': (186, 85, 211),
#     'mediumorchid1': (224, 102, 255), 'mediumpurple': (147, 112, 219), 'mediumpurple1': (171, 130, 255),
#     'mediumseagreen': (60, 179, 113), 'mediumslateblue': (123, 104, 238),
# }

_generates = array(
    [
        (240, 248, 255), (127, 255, 212), (240, 255, 255), (245, 245, 220), (255, 228, 196), (255, 235, 205),
        (0, 0, 255), (176, 196, 222), (224, 102, 255),
        (138, 43, 226), (165, 42, 42), (255, 64, 64), (222, 184, 135), (95, 158, 160), (127, 255, 0), (210, 105, 30),
        (255, 215, 0), (218, 165, 32), (0, 255, 0), (173, 255, 47), (240, 255, 240), (255, 105, 180), (205, 92, 92),
        (75, 0, 130), (255, 255, 240), (135, 206, 250), (176, 226, 255), (132, 112, 255), (119, 136, 153),
        (202, 225, 255), (255, 255, 224), (50, 205, 50), (250, 240, 230), (176, 48, 96), (186, 85, 211),
        (147, 112, 219), (171, 130, 255), (60, 179, 113), (123, 104, 238)
    ]
)
_len = len(_generates)


def generate_color():
    return _generates[random.randint(_len)]


def generate_background(color):
    return tuple(map(lambda val: max(val - 50, 0), color))
