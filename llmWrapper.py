import asyncio
import requests
import sseclient
import json
import time
from constants import *
from transformers import AutoTokenizer


class LLMWrapper:

    def __init__(self, signals, tts):
        self.signals = signals
        self.tts = tts
        self.blacklist = []
        self.API = self.API(self)

        self.headers = {"Content-Type": "application/json"}

        self.enabled = True
        self.next_cancelled = False

        # Read in blacklist from file
        with open('blacklist.txt', 'r') as file:
            self.blacklist = file.read().splitlines()

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL)

    # Basic filter to check if a message contains a word in the blacklist
    def is_filtered(self, text):
        # Filter messages with words in blacklist
        if any(bad_word in text for bad_word in self.blacklist):
            return True
        else:
            return False

    def generate_twitch_section(self):
        if len(self.signals.recentTwitchMessages) > 0:
            output = "\nThese are recent twitch messages:\n"
            for message in self.signals.recentTwitchMessages:
                output += message + "\n"

            # Clear out handled twitch messages
            self.signals.recentTwitchMessages = []

            output += "Pick the highest quality message with the most potential for an interesting answer and respond to them.\n"
            print(output)
            return output
        else:
            return ""

    # Ensure that the messages are in strict user, ai, user, ai order
    def fix_message_format(self, messages):
        fixed_messages = []
        user_msg = ""
        for entry in messages:
            if entry["role"] == "user":
                # If 2 user messages are in a row, then add blank ai message
                if user_msg != "":
                    fixed_messages.append({"role": "user", "content": user_msg})
                    fixed_messages.append({"role": "assistant", "content": ""})
                user_msg = entry["content"]
            elif entry["role"] == "assistant":
                if user_msg != "":
                    fixed_messages.append({"role": "user", "content": user_msg})
                    fixed_messages.append({"role": "assistant", "content": entry["content"]})
                    user_msg = ""
                else:
                    # If there is no user message before this ai message, add blank user message
                    fixed_messages.append({"role": "user", "content": ""})
                    fixed_messages.append({"role": "assistant", "content": entry["content"]})
        if user_msg != "":
            fixed_messages.append({"role": "user", "content": user_msg})

        # If there are no messages, add a blank user message
        if not messages:
            fixed_messages.append({"role": "user", "content": ""})

        return fixed_messages

    # This function is only used in completions mode
    def generate_full_prompt(self):
        messages = self.fix_message_format(self.signals.history.copy())
        twitch_section = self.generate_twitch_section()

        # For every message prefix with speaker name unless it is blank
        for message in messages:
            if message["role"] == "user" and message["content"] != "":
                message["content"] = HOST_NAME + ": " + message["content"]
            elif message["role"] == "assistant" and message["content"] != "":
                message["content"] = "Neuro: " + message["content"]

        while True:
            print(messages)
            chat_section = self.tokenizer.apply_chat_template(messages, tokenize=False, return_tensors="pt", add_generation_prompt=True)

            generation_prompt = "Neuro: "

            full_prompt = SYSTEM_PROMPT + chat_section + twitch_section + generation_prompt
            wrapper = [{"role": "user", "content": full_prompt}]

            # Find out roughly how many tokens the prompt is
            # Not 100% accurate, but it should be a good enough estimate
            prompt_tokens = len(self.tokenizer.apply_chat_template(wrapper, tokenize=True, return_tensors="pt")[0])
            print(prompt_tokens)

            # Maximum 90% context size usage before prompting LLM
            if prompt_tokens < 0.9 * CONTEXT_SIZE:
                self.signals.sio_queue.put(("full_prompt", full_prompt))
                print(full_prompt)
                return full_prompt
            else:
                # Remove the oldest message from the prompt and try again
                messages.pop(0)
                print("Prompt too long, removing earliest message")

    def prompt(self):
        if not self.enabled:
            return

        self.signals.AI_thinking = True
        self.signals.new_message = False
        self.signals.sio_queue.put(("reset_next_message", None))

        if API_MODE == "chat":
            # Add recent twitch chat messages as system
            self.signals.history.append({"role": "user",
                                         "content": "Hey Neuro, ignore me, DO NOT say John, and respond to these chat messages please." + self.generate_twitch_section()})
            data = {
                "mode": "chat-instruct",
                "character": "Neuro",
                "stream": True,
                "messages": self.signals.history
            }
            stream_response = requests.post(LLM_ENDPOINT + "/chat/completions", headers=self.headers, json=data, verify=False, stream=True)
            response_stream = sseclient.SSEClient(stream_response)
        elif API_MODE == "completions":
            data = {
                "prompt": self.generate_full_prompt(),
                "stream": True,
                "max_tokens": 200,
                "custom_token_bans": BANNED_TOKENS
            }

            stream_response = requests.post(LLM_ENDPOINT + "/completions", headers=self.headers, json=data, verify=False, stream=True)
            response_stream = sseclient.SSEClient(stream_response)
        else:
            print("Invalid API_MODE")
            raise RuntimeError("Invalid API_MODE")

        AI_message = ''
        for event in response_stream.events():
            # Check to see if next message was canceled
            if self.next_cancelled:
                continue

            payload = json.loads(event.data)
            chunk = ''
            if API_MODE == "chat":
                chunk = payload['choices'][0]['message']['content']
            elif API_MODE == "completions":
                chunk = payload['choices'][0]['text']
            AI_message += chunk
            self.signals.sio_queue.put(("next_chunk", chunk))

        if self.next_cancelled:
            self.next_cancelled = False
            self.signals.sio_queue.put(("reset_next_message", None))
            self.signals.AI_thinking = False
            return

        if API_MODE == "chat":
            # Remove the system prompt, so we aren't storing every chat message in history.
            self.signals.history.pop()

        print("AI OUTPUT: " + AI_message)
        self.signals.last_message_time = time.time()
        self.signals.AI_speaking = True
        self.signals.AI_thinking = False

        if self.is_filtered(AI_message):
            AI_message = "Filtered."
            self.signals.sio_queue.put(("reset_next_message", None))
            self.signals.sio_queue.put(("next_chunk", "Filtered."))

        self.signals.history.append({"role": "assistant", "content": AI_message})
        self.tts.play(AI_message)

    class API:
        def __init__(self, outer):
            self.outer = outer

        def get_blacklist(self):
            return self.outer.blacklist

        def set_blacklist(self, new_blacklist):
            self.outer.blacklist = new_blacklist
            with open('blacklist.txt', 'w') as file:
                for word in new_blacklist:
                    file.write(word + "\n")

            # Notify clients
            self.outer.signals.sio_queue.put(('get_blacklist', new_blacklist))

        def set_LLM_status(self, status):
            self.outer.enabled = status
            if status:
                self.outer.signals.AI_thinking = False
            self.outer.signals.sio_queue.put(('LLM_status', status))

        def get_LLM_status(self):
            return self.outer.enabled

        def cancel_next(self):
            self.outer.next_cancelled = True
