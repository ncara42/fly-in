from enum import Enum

class Color:
    RED = '\033[31m'
    ERROR = '\033[31m'
    RESET = '\033[0m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    GRAY = '\033[37m'
    ORANGE = '\033[38;5;208m'
    PURPLE = '\033[38;5;129m'
    CYAN = '\033[36m'
    BROWN = '\033[38;5;94m'
    MAGENTA = '\033[35m'
    GOLD = '\033[38;5;220m'
    LIME = '\033[38;5;118m'
    ORANGE = '\033[38;5;208m'
    PURPLE = '\033[38;5;129m'
    BROWN = '\033[38;5;94m'


class Palette(Enum):
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"
    GRAY = "white"
    RED = "red"
    ORANGE = "orange"
    PURPLE = "purple"
    CYAN = "cyan"
    BROWN = "brown"
    MAGENTA = "magenta"
    GOLD = "gold"
    LIME = "lime"


COLOR_MAP = {
    'red': Color.RED,
    'green': Color.GREEN,
    'yellow': Color.YELLOW,
    'blue': Color.BLUE,
    'gray': Color.GRAY,
    'orange': Color.ORANGE,
    'purple': Color.PURPLE,
    'cyan': Color.CYAN,
    'brown': Color.BROWN,
    'magenta': Color.MAGENTA,
    'gold': Color.GOLD,
    'lime': Color.LIME,
    'none': Color.RESET
}
