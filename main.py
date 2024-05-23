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
from modules.audioPlayer import AudioPlayer
from modules.vtubeStudio import VtubeStudio
# from modules.multimodal import MultiModal
from modules.customPrompt import CustomPrompt
from modules.memory import Memory
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

    # MODULES
    # Modules that start disabled CANNOT be enabled while the program is running.
    modules = {}
    module_threads = {}

    # Create STT
    stt = STT(signals)
    # Create TTS
    tts = TTS(signals)
    # Create LLMWrapper
    llm_wrapper = LLMWrapper(signals, tts, modules)
    # Create Prompter
    prompter = Prompter(signals, llm_wrapper)

    # Create Discord bot
    # modules['discord'] = DiscordClient(signals, stt, enabled=False)
    # Create Twitch bot
    modules['twitch'] = TwitchClient(signals, enabled=True)
    # Create audio player
    modules['audio_player'] = AudioPlayer(signals, enabled=True)
    # Create Vtube Studio plugin
    modules['vtube_studio'] = VtubeStudio(signals, enabled=True)
    # Create Multimodal module (Currently no suitable models have been found/created)
    # modules['multimodal'] = MultiModal(signals, enabled=False)
    # Create Custom Prompt module
    modules['custom_prompt'] = CustomPrompt(signals, enabled=True)
    # Create Memory module
    modules['memory'] = Memory(signals, enabled=True)

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

    # Wait for all modules to finish
    for module_thread in module_threads.values():
        module_thread.join()

    sio_thread.join()
    print("SIO EXITED ======================")
    prompter_thread.join()
    print("PROMPTER EXITED ======================")
    # stt_thread.join()
    # print("STT EXITED ======================")

    print("All threads exited, shutdown complete")
    sys.exit(0)

if __name__ == '__main__':
    asyncio.run(main())
