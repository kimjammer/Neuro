# Python Module Imports
import signal
import sys
import time
import threading
import asyncio
# Class Imports
from signals import Signals
from prompter import Prompter
from llmWrapper import LLMWrapper
from stt import STT
from tts import TTS
from modules.twitchClient import TwitchClient
from socketioServer import SocketIOServer


async def main():
    print("Starting Project...")

    # Register signal handler so that all threads can be exited.
    def signal_handler(sig, frame):
        print('Received CTRL + C, attempting to gracefully exit. Close all dashboard windows to speed up shutdown.')
        signals.terminate = True
        stt.API.shutdown()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # CORE FILES

    # Singleton object that every module will be able to read/write to
    signals = Signals()

    # Create STT
    stt = STT(signals)
    # Create TTS
    tts = TTS(signals)
    # Create LLMController
    llm_wrapper = LLMWrapper(signals, tts)
    # Create Prompter
    prompter = Prompter(signals, llm_wrapper)

    # MODULES
    modules = {}
    module_threads = {}

    # Create Discord bot
    # modules['discord'] = DiscordClient(signals, stt, enabled=False)
    # Create Twitch bot
    modules['twitch'] = TwitchClient(signals, enabled=False)

    # Create Socket.io server
    sio = SocketIOServer(signals, stt, tts, llm_wrapper, prompter, modules=modules)

    # Create threads (As daemons, so they exit when the main thread exits)
    prompter_thread = threading.Thread(target=prompter.prompt_loop, daemon=True)
    stt_thread = threading.Thread(target=stt.listen_loop, daemon=True)
    sio_thread = threading.Thread(target=sio.start_server, daemon=True)
    # Start Threads
    sio_thread.start()
    prompter_thread.start()
    stt_thread.start()

    # Create and start threads for modules
    for name, module in modules.items():
        module_thread = threading.Thread(target=module.init_event_loop, daemon=True)
        module_threads[name] = module_thread
        module_thread.start()

    while not signals.terminate:
        time.sleep(0.1)
    print("TERMINATING ======================")

    # Wait for child threads to exit before exiting main thread
    sio_thread.join()
    print("SIO EXITED ======================")
    prompter_thread.join()
    print("PROMPTER EXITED ======================")
    # stt_thread.join()
    # print("STT EXITED ======================")

    # Wait for all modules to finish
    for module_thread in module_threads.values():
        module_thread.join()

    sys.exit(0)

if __name__ == '__main__':
    asyncio.run(main())
