import io
from discord.sinks.core import Filters, Sink, default_filters, AudioData


class StreamingSink(Sink):
    """A custom sink that will convert the audio to 

    """

    def __init__(self, signals, stt, filters=None):
        if filters is None:
            filters = default_filters
        self.filters = filters
        Filters.__init__(self, **self.filters)

        self.encoding = "pcm"
        self.vc = None
        self.audio_data = {}

        self.signals = signals
        self.stt = stt

    # Override the write method to instead stream the audio elsewhere
    @Filters.container
    def write(self, data, user):
        print("Receiving voice")
        if user not in self.audio_data:
            file = io.BytesIO()
            self.audio_data.update({user: AudioData(file)})

        file = self.audio_data[user]
        file.write(data)

        # # Save sound data to AudioSegment object
        # sound = AudioSegment(
        #     # raw audio data (bytes)
        #     data=data,
        #     # 2 byte (16 bit) samples
        #     sample_width=2,
        #     # 48 kHz frame rate
        #     frame_rate=48000,
        #     # stereo
        #     channels=2
        # )
        # # Convert sound to mono
        # sound = sound.set_channels(1)
        # # Convert sound to 16khz
        # sound = sound.set_frame_rate(16000)
        # # Send the 16bit 16khz mono PCM audio data to STT
        # if self.signals.stt_ready:
        #     self.stt.feed_audio(sound.raw_data)
        #     print("FEEDING AUDIO")

    def format_audio(self, audio):
        return
