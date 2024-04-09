import queue


class Signals:
    def __init__(self):
        self._human_speaking = False
        self._AI_speaking = False
        self._AI_thinking = False
        self._last_message_time = 0.0
        self._new_message = False
        self._tts_ready = False
        self._stt_ready = False
        self._recentTwitchMessages = []
        self._history = []

        # This flag indicates to all threads that they should immediately terminate
        self._terminate = False

        self.sio_queue = queue.SimpleQueue()

    @property
    def human_speaking(self):
        return self._human_speaking

    @human_speaking.setter
    def human_speaking(self, value):
        self._human_speaking = value
        self.sio_queue.put(('human_speaking', value))
        if value:
            print("SIGNALS: Human Talking Start")
        else:
            print("SIGNALS: Human Talking Stop")

    @property
    def AI_speaking(self):
        return self._AI_speaking

    @AI_speaking.setter
    def AI_speaking(self, value):
        self._AI_speaking = value
        self.sio_queue.put(('AI_speaking', value))
        if value:
            print("SIGNALS: AI Talking Start")
        else:
            print("SIGNALS: AI Talking Stop")

    @property
    def AI_thinking(self):
        return self._AI_thinking

    @AI_thinking.setter
    def AI_thinking(self, value):
        self._AI_thinking = value
        self.sio_queue.put(('AI_thinking', value))
        if value:
            print("SIGNALS: AI Thinking Start")
        else:
            print("SIGNALS: AI Thinking Stop")

    @property
    def last_message_time(self):
        return self._last_message_time

    @last_message_time.setter
    def last_message_time(self, value):
        self._last_message_time = value

    @property
    def new_message(self):
        return self._new_message

    @new_message.setter
    def new_message(self, value):
        self._new_message = value
        if value:
            print("SIGNALS: New Message")

    @property
    def tts_ready(self):
        return self._tts_ready

    @tts_ready.setter
    def tts_ready(self, value):
        self._tts_ready = value

    @property
    def stt_ready(self):
        return self._stt_ready

    @stt_ready.setter
    def stt_ready(self, value):
        self._stt_ready = value

    @property
    def recentTwitchMessages(self):
        return self._recentTwitchMessages

    @recentTwitchMessages.setter
    def recentTwitchMessages(self, value):
        self._recentTwitchMessages = value
        self.sio_queue.put(('recent_twitch_messages', value))

    @property
    def history(self):
        return self._history

    @history.setter
    def history(self, value):
        self._history = value

    @property
    def terminate(self):
        return self._terminate

    @terminate.setter
    def terminate(self, value):
        self._terminate = value
