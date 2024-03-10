import logging
import time
from RealtimeTTS import TextToAudioStream, CoquiEngine

class TTS:
    def __init__(self, signals):
        self.stream = None
        self.signals = signals
        self.API = self.API(self)
        self.enabled = True

        engine = CoquiEngine(
            use_deepspeed=True,
            voice="./voices/calvinSelected.wav",
            speed=1.1,
            level=logging.ERROR
        )
        tts_config = {
            'on_audio_stream_start': self.audio_started,
            'on_audio_stream_stop': self.audio_ended,
            'level': logging.ERROR
        }
        self.stream = TextToAudioStream(engine, **tts_config)
        self.signals.tts_ready = True

    def play(self, message):
        if not self.enabled:
            return

        self.stream.feed(message)
        self.stream.play_async()

    def stop(self):
        self.stream.stop()

    def audio_started(self):
        self.signals.AI_speaking = True
        print("SIGNALS: AI Talking Start")

    def audio_ended(self):
        self.signals.last_message_time = time.time()
        self.signals.AI_speaking = False
        print("SIGNALS: AI Talking Stop")

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