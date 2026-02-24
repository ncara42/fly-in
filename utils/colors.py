from enum import Enum


class Color:
    """
    ANSI color codes for terminal output.
    Each attribute represents a color or style for visualization.
    """
    BLUE = '\033[34m'
    BROWN = '\033[38;5;94m'
    CRIMSON = '\033[38;5;160m'
    CYAN = '\033[36m'
    ERROR = '\033[31m'
    GOLD = '\033[38;5;220m'
    GRAY = '\033[37m'
    GREEN = '\033[32m'
    LIME = '\033[38;5;118m'
    MAGENTA = '\033[35m'
    ORANGE = '\033[38;5;208m'
    PURPLE = '\033[38;5;129m'
    RED = '\033[31m'
    RESET = '\033[0m'
    YELLOW = '\033[33m'
    SUPER_BRIGHT = '\033[38;5;201m'
    DARKRED = '\033[38;5;52m'
    VIOLET = '\033[38;5;93m'


class Palette(Enum):
    """
    Enum of available color palettes for visualization.
    Values correspond to color names used in the system.
    """
    RAINBOW = "rainbow"
    BLUE = "blue"
    BROWN = "brown"
    CRIMSON = "crimson"
    CYAN = "cyan"
    GOLD = "gold"
    GRAY = "gray"
    GREEN = "green"
    LIME = "lime"
    MAGENTA = "magenta"
    ORANGE = "orange"
    PURPLE = "purple"
    RED = "red"
    YELLOW = "yellow"
    DARKRED = "darkred"
    VIOLET = "violet"


COLOR_MAP = {
    'blue': Color.BLUE,
    'brown': Color.BROWN,
    'crimson': Color.CRIMSON,
    'cyan': Color.CYAN,
    'gold': Color.GOLD,
    'gray': Color.GRAY,
    'green': Color.GREEN,
    'lime': Color.LIME,
    'magenta': Color.MAGENTA,
    'orange': Color.ORANGE,
    'purple': Color.PURPLE,
    'red': Color.RED,
    'yellow': Color.YELLOW,
    'rainbow': Color.SUPER_BRIGHT,
    'darkred': Color.DARKRED,
    'violet': Color.VIOLET,
    'none': Color.RESET
}
