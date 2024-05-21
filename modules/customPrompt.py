from modules.module import Module
from modules.injection import Injection


class CustomPrompt(Module):

    def __init__(self, signals, enabled=True):
        super().__init__(signals, enabled)

        self.API = self.API(self)
        self.prompt_injection.text = ""
        self.prompt_injection.priority = 200

    def get_prompt_injection(self):
        return self.prompt_injection

    async def run(self):
        pass

    class API:
        def __init__(self, outer):
            self.outer = outer

        def set_prompt(self, prompt, priority=200):
            self.outer.prompt_injection.text = prompt
            self.outer.prompt_injection.priority = priority

        def get_prompt(self):
            return {"prompt": self.outer.prompt_injection.text, "priority": self.outer.prompt_injection.priority}
