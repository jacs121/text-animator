import random
from typing import Literal, Callable, Union, Sequence, Iterable, cast
import string
import asyncio
import os

from .colors import ansi_fg256, linear_gradient, rgb_to_ansi256
from .ansi import apply_gradient, apply_style
from .modes import MODES, _mode_handlers
from .events import Event, RepeatEvent
from .flags import AnimatorFlags

PaintType = Union[
    tuple[int,int,int],                       # single RGB
    Sequence[tuple[int,int,int]],             # per-character list/tuple
    tuple[tuple[int,int,int], tuple[int,int,int]],  # gradient start/end
    Callable[[str], Iterable[tuple[int,int,int]]],  # callable returning colors
    None
]

class TextAnimator():
    """
    Master controller.
    """
    
    def __call__(
        self,
        text: str | None = None,
        mode: Union[
            Literal["typewriter", "marquee", "bounce", "scramble", "slide", "static"],
            MODES,
            str,
            None
        ] = None,
        interval: float | None = None,
        paint: PaintType | None = None,
        style=None,
        *,
        flags: AnimatorFlags | None = None,
        reset_events: bool = False,   # <── optional, Qt-like explicit reset
    ):
        # Update only values explicitly provided
        if text is not None:
            self.__text__ = text
        if mode is not None:
            self.__mode__ = mode
        if interval is not None:
            self.__interval__ = interval
        if paint is not None:
            self.__paint__ = paint
        if style is not None:
            self.__style__ = style
        if flags is not None:
            self.__flags__ = flags

        # Events behave like Qt signals → never reset silently
        if reset_events:
            self.on_frame = RepeatEvent()
            self.on_complete = Event()

        return self   # allows chaining: animator(text="X")(interval=0.1)

    def __init__(
        self,
        text: str,
        mode: Union[
            Literal["typewriter", "marquee", "bounce", "scramble", "slide", "static"], MODES, str
        ] = MODES.TYPEWRITER,
        interval: float = 0.05,
        paint: PaintType | None = None,
        style=None,
        *,
        flags: AnimatorFlags = AnimatorFlags.NoFlags
    ):
        self.__text__ = text
        self.__mode__ = mode
        self.__interval__ = interval

        self.__paint__ = paint
        self.__style__ = style
        self.__flags__ = flags

        # events
        self.on_frame = RepeatEvent()     # fires each frame
        self.on_complete = Event()        # fires when animation ends
    
    @property
    def sync(self):
        return self.start()

    # -------------------------
    # Built-in mode executors
    # -------------------------

    async def _mode_typewriter(self):
        for i in range(1, len(self.__text__) + 1):
            yield self.__text__[:i]

    async def _mode_marquee(self):
        t = " " * 10 + self.__text__ + " " * 10
        while True:
            for i in range(len(t)):
                yield t[i:i+30]

    async def _mode_bounce(self):
        while True:
            for i in range(len(self.__text__)):
                yield (" " * i) + self.__text__
            for i in reversed(range(len(self.__text__))):
                yield (" " * i) + self.__text__

    async def _mode_scramble(self):
        final = self.__text__
        charset = string.ascii_letters+string.digits

        for i in range(len(final)):
            for _ in range(3):
                scrambled = (
                    final[:i] +
                    "".join(random.choice(charset) for _ in final[i:])
                )
                yield scrambled
        yield final
    
    async def _mode_slide(self):
        final = self.__text__
        for i in range(len(final)):
            yield final[len(final)-i-1:]
    
    async def _mode_static(self):
        yield self.__text__

    # -------------------------

    def _get_executor(self) -> Callable:
        m = self.__mode__
        
        # Prevent TextConfig objects from being used as modes
        if hasattr(m, 'text') and hasattr(m, 'mode'):
            raise TypeError(
                f"Invalid mode: expected string, enum, or callable, got TextConfig object. "
                f"Did you accidentally pass a TextConfig as the mode parameter? "
                f"TextConfig should be in the texts list, not the mode parameter."
            )

        # Enum
        if isinstance(m, MODES):
            m = m.value

        # Built-ins
        if m == "typewriter":
            return self._mode_typewriter
        if m == "marquee":
            return self._mode_marquee
        if m == "bounce":
            return self._mode_bounce
        if m == "scramble":
            return self._mode_scramble
        if m == "slide":
            return self._mode_slide
        if m == "static":
            return self._mode_static

        # Dynamic mode
        if m in _mode_handlers:
            # Use a closure that properly captures current state
            handler = _mode_handlers[m]
            async def _dynamic_executor():
                async for frame in handler(self.__text__):
                    yield frame
            return _dynamic_executor

        raise ValueError("Unknown mode: " + str(m))

    # -------------------------
    async def start(self):
        executor = self._get_executor()

        try:
            if self.__flags__ & AnimatorFlags.HideCursor:
                print("\033[?25l", end="", flush=True)
            if self.__flags__ & AnimatorFlags.ClearScreenBefore:
                print("\033[2J\033[H", end="", flush=True)
            
            frame_str = ""

            async for frame in executor():
                if frame_str and self.__flags__ & AnimatorFlags.ClearLineBefore:
                    print(f"\r{len(frame_str)*" "}\r", end="", flush=True)
                
                frame_str = frame

                if self.__paint__ is None:
                    # fallback: single ANSI color/style if set
                    if self.__style__:
                        frame_str = apply_style(frame_str, self.__style__)
                else:
                    # callable paint
                    if callable(self.__paint__):
                        colors = self.__paint__(frame_str)
                        frame_str = apply_gradient(frame_str, cast(Iterable[tuple[int,int,int]], colors))

                    # per-character list
                    elif isinstance(self.__paint__, list) or isinstance(self.__paint__, tuple) and isinstance(self.__paint__[0], tuple):
                        # gradient tuple
                        if len(self.__paint__) == 2 and all(isinstance(c, tuple) for c in self.__paint__):
                            start, end = self.__paint__
                            grad = linear_gradient(start, end, len(frame_str))
                            frame_str = apply_gradient(frame_str, grad)
                        else:
                            # explicit per-character
                            if len(self.__paint__) != len(frame_str):
                                raise ValueError("Length of paint list must match text length")
                            frame_str = apply_gradient(frame_str, cast(Iterable[tuple[int,int,int]], self.__paint__))

                    # single RGB
                    elif isinstance(self.__paint__, tuple) and len(self.__paint__)==3:
                        color_index = rgb_to_ansi256(*self.__paint__)
                        frame_str = f"{ansi_fg256(color_index)}{frame_str}\033[0m"

                print("\r" + frame_str, end="", flush=True)

                await self.on_frame.trigger_frame(frame)
                await asyncio.sleep(self.__interval__)

        finally:
            if self.__flags__ & AnimatorFlags.ClearScreenAfter:
                os.system("cls" if os.name == "win" else "clear")

            if self.__flags__ & AnimatorFlags.KeepLastFrame:
                print("\r\033[2K\r", end="")

            if self.__flags__ & AnimatorFlags.ClearLineAfter:
                print(f"\r{len(frame_str)*" "}\r", end="", flush=True)

            if self.__flags__ & AnimatorFlags.AutoNewline:
                print()

            if self.__flags__ & AnimatorFlags.HideCursor:
                print("\033[?25h", end="", flush=True)

            await self.on_complete.emit(self.__text__)
