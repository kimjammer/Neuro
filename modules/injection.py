
'''
Represents some text to be injected into the LLM prompt.
Injections are added to the prompt from lowest to highest priority, with the highest being at the end.
Text is the text to be injected.
Priority is a positive integer. Injections with negative priority will be ignored.
System Prompt Priority: 10
Message History: 50
Twitch Chat: 100
'''


class Injection:
    def __init__(self, text, priority):
        self.text = text
        self.priority = priority

    def __str__(self):
        return self.text
