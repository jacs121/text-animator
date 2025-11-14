from .animator import TextAnimator
from .modes import MODES, register_mode
from .ansi import Style, Color
from .events import Event
from .flags import AnimatorFlags
from .multiline import MultiTextAnimator, MultiTextMode, TextConfig

__all__ = [
    'TextAnimator',
    'MultiTextAnimator',
    'MODES',
    'MultiTextMode',
    'TextConfig',
    'register_mode',
    'Style',
    'Color',
    'Event',
    'AnimatorFlags'
]