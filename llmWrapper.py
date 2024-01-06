import requests
import time


class LLMWrapper:
    url = "http://127.0.0.1:5000/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    signals = None
    history = None
    tts = None

    def __init__(self, signals, history, tts):
        self.signals = signals
        self.history = history
        self.tts = tts

    def is_filtered(self, text):
        # Example filtering algorithm
        if "turkey" in text.lower():
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
        self.signals.AI_thinking = True
        print("SIGNALS: AI Thinking Start")

        # Add recent twitch chat messages as system
        self.history.append({"role": "user",
                             "content": "Hey Neuro, ignore me, DO NOT say John, and respond to these chat messages please." + self.generate_system_prompt()})

        self.signals.new_message = False
        data = {
            "mode": "chat-instruct",
            "character": "Neuro",
            "messages": self.history
        }

        response = requests.post(self.url, headers=self.headers, json=data, verify=False)
        AI_message = response.json()['choices'][0]['message']['content']

        # Remove the system prompt so we aren't storing every chat message in history.
        self.history.pop()

        print("AI OUTPUT: " + AI_message)
        self.signals.last_message_time = time.time()
        self.signals.AI_speaking = True
        self.signals.AI_thinking = False
        print("SIGNALS: AI Thinking Stop")

        if self.is_filtered(AI_message):
            AI_message = "Filtered."

        self.history.append({"role": "assistant", "content": AI_message})
        self.tts.play(AI_message)
