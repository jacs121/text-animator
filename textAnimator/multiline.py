import asyncio
from typing import Literal, Union, Sequence
from enum import Enum

from .animator import TextAnimator, PaintType
from .modes import MODES
from .flags import AnimatorFlags
from .events import Event
from .ansi import apply_gradient, apply_style
from .colors import rgb_to_ansi256, ansi_fg256

class MultiTextMode(Enum):
    """Multi-line animation coordination modes"""
    SIMULTANEOUS = "simultaneous"  # All lines animate at the same time
    STAGGERED = "staggered"        # Lines animate with delay between each
    SEQUENTIAL = "sequential"       # Lines animate one after another (wait for completion)

class TextConfig:
    """Configuration for a single line in multi-line animation"""
    def __init__(self,
            text: str,
            mode: Union[
                Literal["typewriter", "marquee", "bounce", "scramble", "slide"], MODES, str
            ] = MODES.TYPEWRITER,
            interval: float = 0.05,
            paint: PaintType = None,
            style=None,
            flags: AnimatorFlags = AnimatorFlags.NoFlags
        ):

        self.text = text
        self.mode = mode
        self.interval = interval

        self.paint = paint
        self.style = style
        self.flags = flags

class _TextConfigurator:
    """
    Configurator for individual line animations in MultiTextAnimator.
    
    Allows per-line modification through indexing: animator[0](paint=(255, 0, 0))
    """
    
    def __init__(self, multiline_animator: 'MultiTextAnimator', text_index: int):
        self.__multiline__ = multiline_animator
        self.__text_index__ = text_index
    
    def __call__(
        self,
        text: str | None = None,
        mode: Union[Literal["typewriter", "marquee", "bounce", "scramble", "slide"], MODES, str, None] = None,
        interval: float | None = 0.05,
        paint: PaintType = None,
        style = None,
        flags: AnimatorFlags | None = AnimatorFlags.NoFlags,
    ):
        """
        Configure the specific line at this index.
        
        Args:
            text: New text for this line
            mode: Animation mode for this line
            interval: Animation speed for this line
            paint: Color/gradient for this line
            style: Style for this line
            flags: Flags for this line
        
        Returns:
            self for chaining
            
        Example:
            animator[0](texts=["New 1", "New 2"])
            animator[0](paint=(255, 0, 0))
            animator[0](mode=MODES.SCRAMBLE)(interval=0.02)  # Chaining
        """
        if self.__text_index__ >= len(self.__multiline__.__animators__):
            raise IndexError(f"Line index {self.__text_index__} out of range. Only {len(self.__multiline__.__animators__)} lines available.")
        
        # Update the specific line configuration
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
        if flags is not None:
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
        
        # Replace the animator at this index
        self.__multiline__.__animators__[self.__text_index__] = animator
        
        return self  # Enable chaining

class MultiTextAnimator:
    """
    Multi-line text animator with synchronized coordination.
    
    Extends TextAnimator functionality to handle multiple lines with:
    - Simultaneous: All lines animate together
    - Staggered: Lines start with delays
    - Sequential: Lines animate one after another
    - Per-line customization: Each line can have its own mode, colors, style
    - Individual line control: Use animator[0] for per-line configuration
    
    Example:
        animator = MultiTextAnimator(
            lines=["Line 1", "Line 2", "Line 3"],
            coordination=MultiTextMode.STAGGERED,
            default_mode=MODES.TYPEWRITER
        )
        
        # Individual line control
        animator[0](paint=(255, 0, 0))
        animator[0](text="New Text 1")
        animator[1](mode=MODES.MARQUEE)
        
        # Global control
        animator(coordination=MultiTextMode.SIMULTANEOUS)
        animator(default_paint=(0, 255, 0))
        
        await animator.start()
    """
    
    def __getitem__(self, index: int) -> _TextConfigurator:
        """
        Get a configurator for the line at the specified index.
        
        Allows per-line modification through indexing: animator[0](paint=(255, 0, 0))
        
        Args:
            index: Line index (0-based)
        
        Returns:
            _TextConfigurator for modifying that specific line
            
        Example:
            animator[0](paint=(255, 0, 0))
            animator[1](mode=MODES.SCRAMBLE)(text="New text")
        """
        return _TextConfigurator(self, index)
    
    def __call__(
        self,
        texts: Sequence[str | TextConfig] | None = None,
        coordination: MultiTextMode | None = None,
        stagger_delay: float | None = None,
        text_spacing: int | None = None,
        *,
        reset_events: bool = False,
    ):
        """
        Update animation parameters on the fly.
        
        Similar to TextAnimator's __call__, allows runtime modification.
        Only updates values explicitly provided (not None).
        
        For per-line control, use: animator[0](paint=(255, 0, 0))
        
        Args:
            lines: New lines to animate (replaces all existing lines)
            coordination: New coordination mode for global control
            stagger_delay: New stagger delay for global control
            line_spacing: New line spacing for global control
            reset_events: If True, reset event handlers
        
        Returns:
            self for chaining
            
        Example:
            # Individual line control
            animator[0](texts=["New 1", "New 2"])
            animator[0](coordination=MultiTextMode.STAGGERED, stagger_delay=0.3)
            animator[0](paint=(255, 0, 0))(interval=0.02)  # Chaining
            
            # Global control
            animator(coordination=MultiTextMode.SIMULTANEOUS)
            animator(default_paint=(0, 255, 0))(default_interval=0.05)  # Chaining
        """
        # Update coordination settings
        if coordination is not None:
            self.__coordination__ = coordination
        if stagger_delay is not None:
            self.__stagger_delay__ = stagger_delay
        if text_spacing is not None:
            self.__text_spacing__ = text_spacing
        
        # Update lines (requires rebuilding animators)
        if texts is not None:
            # Convert lines to TextConfig objects
            self.__text_configs__: list[TextConfig] = []
            for text in texts:
                if isinstance(text, str):
                    self.__text_configs__.append(TextConfig(text=text))
                else:
                    self.__text_configs__.append(text)
            
            # Rebuild animators for each line
            self.__animators__: list[TextAnimator] = []
            for config in self.__text_configs__:
                animator = TextAnimator(
                    text=config.text,
                    mode=config.mode,
                    interval=config.interval,
                    paint=config.paint,
                    style=config.style,
                    flags=config.flags,
                )
                self.__animators__.append(animator)
            
            # Reset completion counter
            self.__completed_texts__ = 0
        
        # Events behave like Qt signals → never reset silently
        if reset_events:
            self.on_text_complete = Event()
            self.on_all_complete = Event()
        
        return self  # Allows chaining
    
    def __init__(
        self,
        texts: Sequence[str | TextConfig],
        coordination: MultiTextMode = MultiTextMode.SIMULTANEOUS,
        stagger_delay: float = 0.1,
        text_spacing: int = 0,
    ):
        """
        Initialize multi-line animator.
        
        Args:
            lines: List of strings or TextConfig objects
            coordination: How to coordinate multiple line animations
            stagger_delay: Delay between line starts in STAGGERED mode (seconds)
            line_spacing: Number of blank lines between each animated line
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
        
        # Create animators for each line
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
        self.on_text_complete = Event()  # Fires when a line completes
        self.on_all_complete = Event()   # Fires when all lines complete
        
        # State
        self.__completed_texts__ = 0
    
    async def _run_animator_at_text(self, animator: TextAnimator, text_index: int):
        """Run a single animator and render it at a specific line position"""
        executor = animator._get_executor()
        
        try:
            # Calculate vertical position (account for line spacing)
            vertical_offset = text_index * (1 + self.__text_spacing__)
            
            async for frame in executor():
                frame_str = frame
                
                # Apply coloring (same logic as TextAnimator.start)
                if animator.__paint__ is None:
                    if animator.__style__:
                        frame_str = apply_style(frame_str, animator.__style__)
                else:
                    if callable(animator.__paint__):
                        from typing import cast, Iterable
                        colors = animator.__paint__(frame_str)
                        frame_str = apply_gradient(frame_str, cast(Iterable[tuple[int,int,int]], colors))
                    elif isinstance(animator.__paint__, list) or (isinstance(animator.__paint__, tuple) and len(animator.__paint__) > 0 and isinstance(animator.__paint__[0], tuple)):
                        if len(animator.__paint__) == 2 and all(isinstance(c, tuple) and len(c) == 3 for c in animator.__paint__):
                            from .colors import linear_gradient
                            start, end = animator.__paint__
                            grad = linear_gradient(start, end, len(frame_str))
                            frame_str = apply_gradient(frame_str, grad)
                        else:
                            from typing import cast, Iterable
                            if len(animator.__paint__) != len(frame_str):
                                raise ValueError("Length of paint list must match text length")
                            frame_str = apply_gradient(frame_str, cast(Iterable[tuple[int,int,int]], animator.__paint__))
                    elif isinstance(animator.__paint__, tuple) and len(animator.__paint__) == 3:
                        color_index = rgb_to_ansi256(*animator.__paint__)
                        frame_str = f"{ansi_fg256(color_index)}{frame_str}\033[0m"
                
                # Position cursor at the correct line
                print(f"\033[s", end="", flush=True)  # Save cursor position
                if vertical_offset > 0:
                    print(f"\033[{vertical_offset}B", end="", flush=True)  # Move down
                print(f"\r{frame_str}\033[K", end="", flush=True)  # Print and clear to end of line
                print(f"\033[u", end="", flush=True)  # Restore cursor position
                
                await animator.on_frame.trigger_frame(frame)
                await asyncio.sleep(animator.__interval__)
        
        finally:
            # Line completed
            self.__completed_texts__ += 1
            await self.on_text_complete.emit(text_index)
            await animator.on_complete.emit(animator.__text__)
    
    async def start(self):
        """Start the multi-line animation"""
        try:
            # Setup
            if any(a.__flags__ & AnimatorFlags.HideCursor for a in self.__animators__):
                print("\033[?25l", end="", flush=True)
            
            if any(a.__flags__ & AnimatorFlags.ClearScreenBefore for a in self.__animators__):
                print("\033[2J\033[H", end="", flush=True)
            
            # Reserve space for all lines
            total_texts = len(self.__animators__) * (1 + self.__text_spacing__)
            for _ in range(total_texts):
                print()
            if total_texts > 0:
                print(f"\033[{total_texts}A", end="", flush=True)  # Move cursor back to top
            
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
                print("\033[2J\033[H", end="", flush=True)
            
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
            # Add delay before starting each line
            if i > 0:  # Don't delay the first line
                await asyncio.sleep(self.__stagger_delay__)
            task = asyncio.create_task(self._run_animator_at_text(animator, i))
            tasks.append(task)
        
        # Wait for all to complete
        await asyncio.gather(*tasks)
    
    async def _run_sequential(self):
        """Run animations sequentially (one after another)"""
        for i, animator in enumerate(self.__animators__):
            await self._run_animator_at_text(animator, i)
