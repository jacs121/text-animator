import asyncio
from contextlib import asynccontextmanager
from typing import Callable

class Event:
    """
    A simple async event dispatcher.
    `.emit(data)` notifies listeners.
    `async with event.wait():` waits for the next emission.
    """

    def __init__(self):
        self._listeners = []
        self._waiters = []

    def connect(self, func):
        self._listeners.append(func)

    async def emit(self, data=None):
        # call listeners
        for f in self._listeners:
            res = f(data)
            if asyncio.iscoroutine(res):
                await res

        # release any awaiting contexts
        for fut in self._waiters:
            if not fut.done():
                fut.set_result(data)
        self._waiters.clear()

    @asynccontextmanager
    async def wait(self):
        future = asyncio.get_event_loop().create_future()
        self._waiters.append(future)
        result = await future
        yield result

class RepeatEvent(Event):
    """
    Fires automatically every frame (e.g. every iteration of animator loop).
    Animator must call .trigger_frame() each frame.
    """

    async def trigger_frame(self, frame_data=None):
        await self.emit(frame_data)

def on(event: Event):
    def wrapper(func: Callable):
        event.connect(func)
        return func
    return wrapper