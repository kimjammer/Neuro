import os

from transformers import AutoTokenizer
from constants import *
from llmWrappers.abstractLLMWrapper import AbstractLLMWrapper


class TextLLMWrapper(AbstractLLMWrapper):

    def __init__(self, signals, tts, llmState, modules=None):
        super().__init__(signals, tts, llmState, modules)
        self.SYSTEM_PROMPT = SYSTEM_PROMPT
        self.LLM_ENDPOINT = LLM_ENDPOINT
        self.CONTEXT_SIZE = CONTEXT_SIZE
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL, token=os.getenv("HF_TOKEN"))

    def prepare_payload(self):
        return {
            "mode": "instruct",
            "stream": True,
            "max_tokens": 200,
            "skip_special_tokens": False,  # Necessary for Llama 3
            "custom_token_bans": BANNED_TOKENS,
            "stop": STOP_STRINGS,
            "messages": [{
                "role": "user",
                "content": self.generate_prompt()
            }]
        }