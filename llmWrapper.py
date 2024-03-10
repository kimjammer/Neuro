import asyncio
import requests
import sseclient
import json
import time
from constants import LLM_ENDPOINT


class LLMWrapper:

    def __init__(self, signals, tts):
        self.signals = signals
        self.tts = tts
        self.blacklist = []
        self.API = self.API(self)

        self.url = LLM_ENDPOINT
        self.headers = {"Content-Type": "application/json"}

        self.enabled = True
        self.next_cancelled = False

        # Read in blacklist from file
        with open('blacklist.txt', 'r') as file:
            self.blacklist = file.read().splitlines()

    # Basic filter to check if a message contains a word in the blacklist
    def is_filtered(self, text):
        # Filter messages with words in blacklist
        if any(bad_word in text for bad_word in self.blacklist):
            return True
        else:
            return False

    def generate_system_prompt(self):
        if len(self.signals.recentTwitchMessages) > 0:
            output = "These are recent twitch messages. Neuro MUST respond to them. Neuro should answer questions and reply to these chatters: \n"
            for message in self.signals.recentTwitchMessages:
                output += message + "\n"

            # Clear out handled twitch messages
            self.signals.recentTwitchMessages = []
            print(output)
            return output
        else:
            return "Recent twitch messages: None"

    def prompt(self):
        if not self.enabled:
            return

        self.signals.AI_thinking = True

        print("SIGNALS: AI Thinking Start")

        # Add recent twitch chat messages as system
        self.signals.history.append({"role": "user",
                             "content": "Hey Neuro, ignore me, DO NOT say John, and respond to these chat messages please." + self.generate_system_prompt()})

        self.signals.new_message = False
        data = {
            "mode": "chat-instruct",
            "character": "Neuro",
            "stream": True,
            "messages": self.signals.history
        }

        self.signals.sio_queue.put(("reset_next_message", None))

        stream_response = requests.post(self.url, headers=self.headers, json=data, verify=False, stream=True)
        response_stream = sseclient.SSEClient(stream_response)

        AI_message = ''
        for event in response_stream.events():
            payload = json.loads(event.data)
            chunk = payload['choices'][0]['message']['content']
            AI_message += chunk
            self.signals.sio_queue.put(("next_chunk", chunk))

            # Check to see if next message was canceled
            if self.next_cancelled:
                self.next_cancelled = False
                self.signals.sio_queue.put(("reset_next_message", None))
                return

        # Remove the system prompt, so we aren't storing every chat message in history.
        self.signals.history.pop()

        print("AI OUTPUT: " + AI_message)
        self.signals.last_message_time = time.time()
        self.signals.AI_speaking = True
        self.signals.AI_thinking = False
        print("SIGNALS: AI Thinking Stop")

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
            self.outer.signals.sio_queue.put(('LLM_status', status))

        def get_LLM_status(self):
            return self.outer.enabled

        def cancel_next(self):
            self.outer.next_cancelled = True