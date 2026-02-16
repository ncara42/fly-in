from colored import fg, attr
from enum import Enum

class Color:
    ERROR = fg('red')
    RESET = attr('reset')
    GREEN = fg('green')
    YELLOW = fg('yellow')
    BLUE = fg('blue')
    GRAY = fg('white')


class Palette(Enum):
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"
    GRAY = "white"
    RED = "red"
