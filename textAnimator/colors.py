# Terminal ANSI 256-color helper
def rgb_to_ansi256(r: int, g: int, b: int) -> int:
    """
    Convert 0-255 RGB to nearest 256-color ANSI index
    """
    r = max(0, min(5, int(r / 256 * 6)))
    g = max(0, min(5, int(g / 256 * 6)))
    b = max(0, min(5, int(b / 256 * 6)))
    return 16 + 36 * r + 6 * g + b

def ansi_fg256(index: int) -> str:
    return f"\033[38;5;{index}m"

def ansi_bg256(index: int) -> str:
    return f"\033[48;5;{index}m"

# -----------------------
# ColorSpace conversions
# -----------------------

def from_rgb(r: int, g: int, b: int) -> tuple[int, int, int]:
    return (r, g, b)


def from_hex(hexstr: str) -> tuple[int, int, int]:
    hexstr = hexstr.lstrip("#")
    return (int(hexstr[0:2], 16), int(hexstr[2:4], 16), int(hexstr[4:6], 16))


def from_hsv(h: float, s: float, v: float) -> tuple[int, int, int]:
    """
    HSV to RGB conversion, h in [0,360], s,v in [0,1]
    """
    h = h % 360
    s = max(0, min(1, s))
    v = max(0, min(1, v))
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if h < 60:
        rp, gp, bp = c, x, 0
    elif h < 120:
        rp, gp, bp = x, c, 0
    elif h < 180:
        rp, gp, bp = 0, c, x
    elif h < 240:
        rp, gp, bp = 0, x, c
    elif h < 300:
        rp, gp, bp = x, 0, c
    else:
        rp, gp, bp = c, 0, x

    r, g, b = (int((rp + m) * 255), int((gp + m) * 255), int((bp + m) * 255))
    return r, g, b

# -----------------------
# Gradient generators
# -----------------------

def linear_gradient(start_rgb: tuple[int,int,int], end_rgb: tuple[int,int,int], n: int) -> list[tuple[int,int,int]]:
    gradient = []
    for i in range(n):
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * i / max(n-1, 0.00001))
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * i / max(n-1, 0.00001))
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * i / max(n-1, 0.00001))
        gradient.append((r,g,b))
    return gradient  # type list