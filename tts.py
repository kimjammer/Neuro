import time
from RealtimeTTS import TextToAudioStream, CoquiEngine
from constants import *


class TTS:
    def __init__(self, signals):
        self.stream = None
        self.signals = signals
        self.API = self.API(self)
        self.enabled = True

        engine = CoquiEngine(
            use_deepspeed=True,
            voice="./voices/" + VOICE_REFERENCE,
            speed=1.1,
        )
        tts_config = {
            'on_audio_stream_start': self.audio_started,
            'on_audio_stream_stop': self.audio_ended,
            'output_device_index': OUTPUT_DEVICE_INDEX,
        }
        self.stream = TextToAudioStream(engine, **tts_config)
        self.signals.tts_ready = True

    def play(self, message):
        if not self.enabled:
            return

        # If the message is only whitespace, don't attempt to play it
        if not message.strip():
            return

        self.signals.sio_queue.put(("current_message", message))
        self.stream.feed(message)
        self.stream.play_async()

    def stop(self):
        self.stream.stop()
        self.signals.AI_speaking = False

    def audio_started(self):
        self.signals.AI_speaking = True

    def audio_ended(self):
        self.signals.last_message_time = time.time()
        self.signals.AI_speaking = False

    class API:
        def __init__(self, outer):
            self.outer = outer

        def set_TTS_status(self, status):
            self.outer.enabled = status
            if not status:
                self.outer.stop()
            self.outer.signals.sio_queue.put(('TTS_status', status))

        def get_TTS_status(self):
            return self.outer.enabled

        def abort_current(self):
            self.outer.stop()
