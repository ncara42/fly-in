from colored import fg, attr
from enum import Enum


class Color:
    RED = fg('red')
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


COLOR_MAP = {
    'red': Color.RED,
    'green': Color.GREEN,
    'yellow': Color.YELLOW,
    'blue': Color.BLUE,
    'gray': Color.GRAY,
    'none': Color.RESET
}
