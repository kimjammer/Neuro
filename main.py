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

if __name__ == '__main__':
    print("Starting Project...")

    # Register signal handler so that all threads can be exited.
    def signal_handler(sig, frame):
        print('Received CTRL + C, attempting to gracefully exit')
        #asyncio.create_task(twitchClient.shutdown())
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    # Create Socket.io server
    sio = SocketIOServer()

    # Singleton object that every module will be able to read/write to
    signals = Signals(sio)
    history = []

    # Create STT
    stt = STT(signals, history, sio)
    # Create TTS
    tts = TTS(signals, sio)
    # Create LLMController
    llmWrapper = LLMWrapper(signals, history, tts, sio)
    # Create Prompter
    prompter = Prompter(signals, llmWrapper, sio)

    # Create Discord bot
    # discordClient = DiscordClient(signals, stt)
    # Create Twitch bot
    twitchClient = TwitchClient(signals)

    # Create Socket.io server
    web_app = sio.start_server(signals, history, stt, tts, llmWrapper, prompter, twitchClient)

    # Create threads (As daemons, so they exit when the main thread exits)
    prompterThread = threading.Thread(target=prompter.prompt_loop, daemon=True)
    sttThread = threading.Thread(target=stt.listen_loop, daemon=True)
    sioThread = threading.Thread(target=sio.init_event_loop, daemon=True)

    # Start Threads
    sioThread.start()
    print("Waiting for sio to start...")
    time.sleep(1)
    prompterThread.start()
    sttThread.start()
    # discordClient.run()
    # Start Twitch bot
    asyncio.run(twitchClient.start_twitch_bot())

    # Run socket.io server
    web.run_app(web_app)

    # Prevent main thread from exiting.
    input()
