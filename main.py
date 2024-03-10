# Python Module Imports
import signal
import sys
import time
import threading
import asyncio
from aiohttp import web
# Class Imports
from signals import Signals
from prompter import Prompter
from llmWrapper import LLMWrapper
from stt import STT
from tts import TTS
from discordClient import DiscordClient
from twitchClient import TwitchClient
from socketioServer import SocketIOServer


async def main():
    print("Starting Project...")

    # Register signal handler so that all threads can be exited.
    def signal_handler(sig, frame):
        print('Received CTRL + C, attempting to gracefully exit')
        #twitchClient.API.terminate()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    # Singleton object that every module will be able to read/write to
    signals = Signals()

    # Create STT
    stt = STT(signals)
    # Create TTS
    tts = TTS(signals)
    # Create LLMController
    llmWrapper = LLMWrapper(signals, tts)
    # Create Prompter
    prompter = Prompter(signals, llmWrapper)

    # Create Discord bot
    # discordClient = DiscordClient(signals, stt)
    # Create Twitch bot
    twitchClient = TwitchClient(signals)

    # Create Socket.io server
    sio = SocketIOServer(signals, stt, tts, llmWrapper, prompter, twitchClient)

    # Create threads (As daemons, so they exit when the main thread exits)
    prompter_thread = threading.Thread(target=prompter.prompt_loop, daemon=True)
    stt_thread = threading.Thread(target=stt.listen_loop, daemon=True)
    sio_thread = threading.Thread(target=sio.start_server, daemon=True)
    twitch_thread = threading.Thread(target=twitchClient.init_event_loop, daemon=True)

    # Start Threads
    sio_thread.start()
    prompter_thread.start()
    stt_thread.start()
    # discordClient.run()
    # Start Twitch bot
    twitch_thread.start()

    # Prevent main thread from exiting.
    input()

if __name__ == '__main__':
    asyncio.run(main())
