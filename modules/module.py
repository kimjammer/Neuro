import asyncio
from modules.injection import Injection

'''
An extendable class that defines a module that interacts with the main program.
All modules will be run in its own thread with its own event loop.
Do not use this class directly, extend it
'''


class Module:

    def __init__(self, signals, enabled=True):
        self.signals = signals
        self.enabled = enabled

        self.prompt_injection = Injection("", -1)

    def init_event_loop(self):
        asyncio.run(self.run())

    def get_prompt_injection(self):
        return self.prompt_injection

    # Function that is called after all modules have provided their injections
    def cleanup(self):
        pass

    async def run(self):
        pass
