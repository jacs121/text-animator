import asyncio
import sys
from typing import Literal, Union, Sequence
from enum import Enum
import os, io
from contextlib import redirect_stdout

from typing import cast, Iterable
from .animator import TextAnimator, PaintType
from .modes import MODES
from .flags import AnimatorFlags
from .events import Event
from .ansi import apply_gradient, apply_style
from .colors import ansi_fg256, linear_gradient, rgb_to_ansi256

class MultiTextMode(Enum):
    """Multi-text animation coordination modes"""
    SIMULTANEOUS = "simultaneous"  # All lines animate at the same time
    STAGGERED = "staggered"        # Lines animate with delay between each
    SEQUENTIAL = "sequential"       # Lines animate one after another (wait for completion)

class TextConfig:
    """Configuration for a single text in multi-text animation"""
    def __init__(self,
            text: str,
            mode: Union[
                Literal["typewriter", "marquee", "bounce", "scramble", "slide", "static"], MODES, str
            ] = MODES.TYPEWRITER,
            interval: float = 0.05,
            paint: PaintType = None,
            style=None,
            flags: AnimatorFlags = AnimatorFlags.NoFlags
        ):
        # Validate that mode is not a TextConfig object
        if hasattr(mode, 'text') and hasattr(mode, 'mode'):
            raise TypeError(
                f"Invalid mode: expected string, enum, or callable, got TextConfig object. "
                f"Did you accidentally nest TextConfig objects?"
            )

        self.text = text
        self.mode = mode
        self.interval = interval

        self.paint = paint
        self.style = style
        self.flags = flags

class _TextConfigurator:
    """
    Configurator for individual text animations in MultiTextAnimator.
    
    Allows per-text modification through indexing: animator[0](paint=(255, 0, 0))
    """
    
    def __init__(self, multiline_animator: 'MultiTextAnimator', text_index: int | slice):
        self.__multiline__ = multiline_animator
        self.__text_index__ = text_index
    
    def __call__(
        self,
        text: str | None = None,
        mode: Union[Literal["typewriter", "marquee", "bounce", "scramble", "slide", "static"], MODES, str, None] = None,
        interval: float | None = 0.05,
        paint: PaintType = None,
        style = None,
        flags: AnimatorFlags = AnimatorFlags.NONE,
    ):
        """
        Configure the specific text at this index.
        
        Args:
            text: New text for this text
            mode: Animation mode for this text
            interval: Animation speed for this text
            paint: Color/gradient for this text
            style: Style for this text
            flags: Flags for this text
        
        Returns:
            self for chaining
            
        Example:
            animator[0](texts=["New 1", "New 2"])
            animator[0](paint=(255, 0, 0))
            animator[0](mode=MODES.SCRAMBLE)(interval=0.02)  # Chaining
        """
        if isinstance(self.__text_index__, int):
            if self.__text_index__ >= len(self.__multiline__.__animators__):
                raise IndexError(f"Text index {self.__text_index__} out of range. Only {len(self.__multiline__.__animators__)} lines available.")
            # Update the specific text configuration
            config = self.__multiline__.__text_configs__[self.__text_index__]
            
            # Update provided parameters
            if text is not None:
                config.text = text
            if mode is not None:
                config.mode = mode
            if interval is not None:
                config.interval = interval
            if paint is not None:
                config.paint = paint
            if style is not None:
                config.style = style
            if not flags & AnimatorFlags.NONE:
                config.flags = flags
            
            # Rebuild the specific animator
            animator = TextAnimator(
                text=config.text,
                mode=config.mode,
                interval=config.interval,
                paint=config.paint,
                style= config.style,
                flags=config.flags
            )
            
            self.__multiline__.__animators__[self.__text_index__] = animator
        elif isinstance(self.__text_index__, slice):
            for i in range(self.__text_index__.start or 0, self.__text_index__.stop, self.__text_index__.step or 1):
                if i >= len(self.__multiline__.__animators__):
                    raise IndexError(f"Text index {i} out of range. Only {len(self.__multiline__.__animators__)} lines available.")
                # Update the specific text configuration
                config = self.__multiline__.__text_configs__[i]
                
                # Update provided parameters
                if text is not None:
                    config.text = text
                if mode is not None:
                    config.mode = mode
                if interval is not None:
                    config.interval = interval
                if paint is not None:
                    config.paint = paint
                if style is not None:
                    config.style = style
                if not flags & AnimatorFlags.NONE:
                    config.flags = flags
                
                # Rebuild the specific animator
                animator = TextAnimator(
                    text=config.text,
                    mode=config.mode,
                    interval=config.interval,
                    paint=config.paint,
                    style= config.style,
                    flags=config.flags
                )
                self.__multiline__.__animators__[i] = animator
        return self  # Enable chaining

class MultiTextAnimator:
    """
    Multi-text text animator with synchronized coordination.
    
    Extends TextAnimator functionality to handle multiple lines with:
    - Simultaneous: All lines animate together
    - Staggered: Lines start with delays
    - Sequential: Lines animate one after another
    - Per-text customization: Each text can have its own mode, colors, style
    - Individual text control: Use animator[0] for per-text configuration
    
    Example:
        animator = MultiTextAnimator(
            lines=["Text 1", "Text 2", "Text 3"],
            coordination=MultiTextMode.STAGGERED,
            default_mode=MODES.TYPEWRITER
        )
        
        # Individual text control
        animator[0](paint=(255, 0, 0))
        animator[0](text="New Text 1")
        animator[1](mode=MODES.MARQUEE)
        
        # Global control
        animator(coordination=MultiTextMode.SIMULTANEOUS)
        animator(default_paint=(0, 255, 0))
        
        await animator.start()
    """
    
    def __getitem__(self, index: int | slice) -> _TextConfigurator:
        """
        Get a configurator for the text at the specified index.
        
        Allows per-text modification through indexing/slicing: animator[0](paint=(255, 0, 0))
        
        Args:
            index: Text index/slice (0-based)
        
        Returns:
            _TextConfigurator for modifying that specific text
            
        Example:
            animator[0](paint=(255, 0, 0))
            animator[1](mode=MODES.SCRAMBLE)(text="New text")
        """
        return _TextConfigurator(self, index)

    def __init__(
        self,
        texts: Sequence[str | TextConfig],
        coordination: MultiTextMode = MultiTextMode.SIMULTANEOUS,
        stagger_delay: float = 0.1,
        text_spacing: int = 0,
    ):
        """
        Initialize multi-text animator.
        
        Args:
            lines: List of strings or TextConfig objects
            coordination: How to coordinate multiple text animations
            stagger_delay: Delay between text starts in STAGGERED mode (seconds)
            line_spacing: Number of blank lines between each animated text
        """
        self.__coordination__ = coordination
        self.__stagger_delay__ = stagger_delay
        self.__text_spacing__ = text_spacing
        # Convert lines to TextConfig objects
        self.__text_configs__: list[TextConfig] = []
        for text in texts:
            if isinstance(text, str):
                self.__text_configs__.append(TextConfig(text=text))
            else:
                self.__text_configs__.append(text)
        
        # Create animators for each text
        self.__animators__: list[TextAnimator] = []
        for config in self.__text_configs__:
            animator = TextAnimator(
                text=config.text,
                mode=config.mode,
                interval=config.interval,
                paint=config.paint,
                style=config.style,
                flags=config.flags
            )
            self.__animators__.append(animator)
        
        # Events
        self.on_text_complete = Event()  # Fires when a text completes
        self.on_all_complete = Event()   # Fires when all lines complete
        
        # State
        self.__completed_texts__ = 0

    @property
    def sync(self):
        return self.start()
    
    async def _run_animator_at_text(self, animator: TextAnimator, text_index: int):
        """Run a single animator and render it at a specific text position"""
        executor = animator._get_executor()
        # Create a string buffer
        # Save the current stdout and redirect it to the buffer
        try:
            # Calculate vertical position (account for text spacing)
            vertical_offset = text_index * (1 + self.__text_spacing__)
            
            async for frame in executor():
                frame_str = frame
                # Position cursor at the correct text
                print(f"\033[s", end="", flush=True)  # Save cursor position
                if vertical_offset > 0:
                    print(f"\033[{vertical_offset}B", end="", flush=True)  # Move down
                
                if animator.__flags__ & AnimatorFlags.HideCursor:
                    print("\033[?25l", end="", flush=True)
                if animator.__flags__ & AnimatorFlags.ClearLineBefore:
                    print("\r", end="", flush=True)
                    
                # Apply coloring (same logic as TextAnimator.start)
                if animator.__paint__ is None:
                    if animator.__style__:
                        frame_str = apply_style(frame_str, animator.__style__)
                else:
                    if callable(animator.__paint__):
                        colors = animator.__paint__(frame_str)
                        frame_str = apply_gradient(frame_str, cast(Iterable[tuple[int,int,int]], colors))
                    elif isinstance(animator.__paint__, list) or (isinstance(animator.__paint__, tuple) and len(animator.__paint__) > 0 and isinstance(animator.__paint__[0], tuple)):
                        if len(animator.__paint__) == 2 and all(isinstance(c, tuple) and len(c) == 3 for c in animator.__paint__):
                            start, end = animator.__paint__
                            grad = linear_gradient(start, end, len(frame_str))
                            frame_str = apply_gradient(frame_str, grad)
                        else:
                            if len(animator.__paint__) != len(frame_str):
                                raise ValueError("Length of paint list must match text length")
                            frame_str = apply_gradient(frame_str, cast(Iterable[tuple[int,int,int]], animator.__paint__))
                    elif isinstance(animator.__paint__, tuple) and len(animator.__paint__) == 3:
                        color_index = rgb_to_ansi256(*animator.__paint__)
                        frame_str = f"{ansi_fg256(color_index)}{frame_str}\033[0m"
                
                print(f"\r{frame_str}\033[K", end="", flush=True)  # Print and clear to end of text
                print("\033[u", end="", flush=True)
                
                await animator.on_frame.trigger_frame(frame)
                await asyncio.sleep(animator.__interval__)
                
                if animator.__flags__ & AnimatorFlags.KeepLastFrame:
                    print("\r\033[2K\r", end="", flush=True)
            if not animator.__flags__ & AnimatorFlags.ClearLineAfter:
                print('\x1b[4A', end="", flush=True)
                print("\b", end="", flush=True)
        finally:
            # Text completed
            self.__completed_texts__ += 1
            await self.on_text_complete.emit(text_index)
            await animator.on_complete.emit(animator.__text__)
    
    async def start(self):
        """Start the multi-text animation"""
        try:
            # Setup
            if any(a.__flags__ & AnimatorFlags.HideCursor for a in self.__animators__):
                print("\033[?25l", end="", flush=True)
            
            if any(a.__flags__ & AnimatorFlags.ClearScreenBefore for a in self.__animators__):
                os.system("cls" if os.name == "win" else "clear")

            # Run animations based on coordination mode
            if self.__coordination__ == MultiTextMode.SIMULTANEOUS:
                await self._run_simultaneous()
            elif self.__coordination__ == MultiTextMode.STAGGERED:
                await self._run_staggered()
            elif self.__coordination__ == MultiTextMode.SEQUENTIAL:
                await self._run_sequential()
        
        finally:
            # Cleanup
            total_texts = len(self.__animators__) * (1 + self.__text_spacing__)
            if total_texts > 0:
                print(f"\033[{total_texts}B", end="", flush=True)  # Move to bottom
            
            if any(a.__flags__ & AnimatorFlags.ClearScreenAfter for a in self.__animators__):
                os.system("cls" if os.name == "win" else "clear")
            
            if any(a.__flags__ & AnimatorFlags.AutoNewline for a in self.__animators__):
                print()
            
            if any(a.__flags__ & AnimatorFlags.HideCursor for a in self.__animators__):
                print("\033[?25h", end="", flush=True)
            
            await self.on_all_complete.emit(None)
    
    async def _run_simultaneous(self):
        """Run all animations simultaneously"""
        tasks = [
            self._run_animator_at_text(animator, i)
            for i, animator in enumerate(self.__animators__)
        ]
        await asyncio.gather(*tasks)
    
    async def _run_staggered(self):
        """Run animations with staggered start times"""
        tasks = []
        for i, animator in enumerate(self.__animators__):
            # Add delay before starting each text
            if i > 0:  # Don't delay the first text
                await asyncio.sleep(self.__stagger_delay__)
            task = asyncio.create_task(self._run_animator_at_text(animator, i))
            tasks.append(task)
        
        # Wait for all to complete
        await asyncio.gather(*tasks)
    
    async def _run_sequential(self):
        """Run animations sequentially (one after another)"""
        for i, animator in enumerate(self.__animators__):
            await self._run_animator_at_text(animator, i)
