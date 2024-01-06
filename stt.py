import logging
import time
from RealtimeSTT import AudioToTextRecorder


class STT:
    signals = None
    history = None
    recorder = None

    def __init__(self, signals, history):
        self.signals = signals
        self.history = history

    def process_text(self, text):
        print("STT OUTPUT: " + text)
        self.history.append({"role": "user", "content": text})

        self.signals.last_message_time = time.time()
        self.signals.new_message = True
        print("SIGNALS: New Message")

    def recording_start(self):
        print("SIGNALS: Human Talking Start")
        self.signals.human_speaking = True

    def recording_stop(self):
        print("SIGNALS: Human Talking Stop")
        self.signals.human_speaking = False

    def feed_audio(self, data):
        self.recorder.feed_audio(data)

    def listen_loop(self):
        recorder_config = {
            'spinner': False,
            'model': 'tiny.en',
            'language': 'en',
            'use_microphone': True,
            'silero_sensitivity': 0.4,
            'silero_use_onnx': True,
            'webrtc_sensitivity': 2,
            'post_speech_silence_duration': 0.4,
            'min_length_of_recording': 0,
            'min_gap_between_recordings': 0,
            'enable_realtime_transcription': True,
            'realtime_processing_pause': 0.2,
            'realtime_model_type': 'tiny.en',
            'on_recording_start': self.recording_start,
            'on_recording_stop': self.recording_stop,
            'level': logging.ERROR
        }

        with AudioToTextRecorder(**recorder_config) as recorder:
            self.recorder = recorder
            print("STT Ready")
            self.signals.stt_ready = True
            while True:
                recorder.text(self.process_text)
