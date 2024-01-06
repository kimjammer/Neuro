import time


class Prompter:
    signals = None
    llmWrapper = None

    system_ready = False
    timeSinceLastMessage = 0.0

    def __init__(self, signals, llmWrapper):
        self.signals = signals
        self.llmWrapper = llmWrapper

    def prompt_now(self):
        # Don't prompt AI if system isn't ready yet
        if not self.signals.stt_ready or not self.signals.tts_ready:
            return False
        # Don't prompt AI when anyone is currently talking
        if self.signals.human_speaking or self.signals.AI_thinking or self.signals.AI_speaking:
            return False
        # Prompt AI if human said something
        if self.signals.new_message:
            return True
        # Prompt AI if there are unprocessed chat messages
        if len(self.signals.recentTwitchMessages) > 0:
            return True
        # Prompt if 15 seconds have passed without anyone talking
        if self.timeSinceLastMessage > 60:
            return True

    def prompt_loop(self):
        while True:
            # Set lastMessageTime to now if program is still starting
            if self.signals.last_message_time == 0.0 or (not self.signals.stt_ready or not self.signals.tts_ready):
                self.signals.last_message_time = time.time()
                self.timeSinceLastMessage = 0.0
            else:
                if not self.system_ready:
                    print("SYSTEM READY")
                    self.system_ready = True

            # Calculate and set time since last message
            self.timeSinceLastMessage = time.time() - self.signals.last_message_time

            # Decide and prompt LLM
            if self.prompt_now():
                print("PROMPTING AI")
                self.llmWrapper.prompt()

            # Sleep for 0.1 seconds before checking again.
            time.sleep(0.1)
            # time.sleep(1)
