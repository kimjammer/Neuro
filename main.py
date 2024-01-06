# Python Module Imports
import signal
import sys
import threading
import asyncio
# Class Imports
from signals import Signals
from prompter import Prompter
from llmWrapper import LLMWrapper
from stt import STT
from tts import TTS
from discordClient import DiscordClient
from twitchClient import TwitchClient

if __name__ == '__main__':
    print("Starting Project...")


    # Register signal handler so that all threads can be exited.
    def signal_handler(sig, frame):
        print('Received CTRL + C, attempting to gracefully exit')
        asyncio.run(twitchClient.shutdown())
        sys.exit(0)


    signal.signal(signal.SIGINT, signal_handler)

    # Singleton object that every module will be able to read/write to
    signals = Signals()
    history = []

    # Create STT
    stt = STT(signals, history)
    # Create TTS
    tts = TTS(signals)
    # Create LLMController
    llmWrapper = LLMWrapper(signals, history, tts)
    # Create Prompter
    prompter = Prompter(signals, llmWrapper)

    # Create Discord bot
    # discordClient = DiscordClient(signals, stt)
    # Create Twitch bot
    twitchClient = TwitchClient(signals)

    # Create threads (As daemons so they exit when the main thread exits)
    prompterThread = threading.Thread(target=prompter.prompt_loop, daemon=True)
    sttThread = threading.Thread(target=stt.listen_loop, daemon=True)

    # Start Threads
    prompterThread.start()
    sttThread.start()
    # discordClient.run()
    # Start Twitch bot
    asyncio.run(twitchClient.start_twitch_bot())

    # Prevent main thread from exiting.
    input()
