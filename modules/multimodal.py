from modules.module import Module
from constants import MULTIMODAL_STRATEGY

class MultiModal(Module):

    def __init__(self, signals, enabled=True):
        super().__init__(signals, enabled)
        self.API = self.API(self)
        self.enabled = enabled


    def get_prompt_injection(self):
        return self.prompt_injection

    async def run(self):
        pass

    def strategy_never(self):
        return False

    def strategy_always(self):
        return True

    class API:
        def __init__(self, outer):
            self.outer = outer

        def set_multimodal_status(self, status):
            self.outer.enabled = status
            self.outer.signals.sio_queue.put(('multimodal_status', status))

        def get_multimodal_status(self):
            return self.outer.enabled

        # Determines when a prompt should go to the multimodal model
        def multimodal_now(self):
            if not self.outer.enabled:
                return False

            if MULTIMODAL_STRATEGY == "never":
                return self.outer.strategy_never()
            elif MULTIMODAL_STRATEGY == "always":
                return self.outer.strategy_always()
            else:
                return False
