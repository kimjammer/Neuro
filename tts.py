import logging
import time
from RealtimeTTS import TextToAudioStream, CoquiEngine


class TTS:
    signals = None
    stream = None

    def __init__(self, signals):
        self.signals = signals

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
