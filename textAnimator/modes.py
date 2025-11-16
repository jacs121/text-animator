from enum import Enum
from typing import Callable, Dict

class MODES(Enum):
    TYPEWRITER = "typewriter"
    MARQUEE = "marquee"
    BOUNCE = "bounce"
    SCRAMBLE = "scramble"
    STATIC = "static"

# Dynamic registry
_mode_handlers: Dict[str, Callable] = {}

def register_mode(name: str):
    """
    Decorator version:

    @register_mode("reversewave")
    async def reverse_wave(text):
        ...
    """
    def wrapper(func: Callable):
        _mode_handlers[name] = func
        return func
    return wrapper


def get_mode(name: str):
    # Try enum
    try:
        return MODES(name.upper())
    except Exception:
        pass

    # Try dynamic mode
    if name in _mode_handlers:
        return _mode_handlers[name]

    raise ValueError(f"Unknown mode: {name}")
