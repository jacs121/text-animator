from typing import Iterable
from enum import Enum
from .colors import rgb_to_ansi256, ansi_fg256

class Color(Enum):
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    BLUE = (0, 0, 255)
    MAGENTA = (255, 0, 255)
    CYAN = (0, 255, 255)
    WHITE = (255, 255, 255)

class Style(Enum):
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"

def apply_gradient(text: str, colors: Iterable[tuple[int,int,int]] | list[tuple[int,int,int]]) -> str:
    """
    Apply per-character colors to text
    colors: list of RGB tuples matching length of text
    """
    colors = list(colors)  # ensure len() works
    if len(text) != len(colors):
        raise ValueError("Text length must equal colors length")

    result = ""
    for ch, (r,g,b) in zip(text, colors):
        result += f"{ansi_fg256(rgb_to_ansi256(r,g,b))}{ch}"
    return result + "\033[0m"

def apply_style(text: str, *codes: Style) -> str:
    if not codes:
        return text
    return "".join([code.value for code in codes]) + text + Style.RESET.value
