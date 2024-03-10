import asyncio
import time
from aiohttp import web
import socketio
from constants import PATIENCE


class SocketIOServer:
    def __init__(self, signals, stt, tts, llmWrapper, prompter, twitchClient):
        self.signals = signals
        self.stt = stt
        self.tts = tts
        self.llmWrapper = llmWrapper
        self.prompter = prompter
        self.twitchClient = twitchClient

    def start_server(self):
        print("Starting Socket.io server")
        sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
        # This removes the delay in the socket.io connection for whatever reason
        # sio.instrument(auth={
        #     'username': 'admin',
        #     'password': 'admin',
        # })
        app = web.Application()
        sio.attach(app)

        @sio.event
        async def get_blacklist(sid):
            await sio.emit('get_blacklist', self.llmWrapper.API.get_blacklist())

        @sio.event
        async def set_blacklist(sid, message):
            self.llmWrapper.API.set_blacklist(message)

        @sio.event
        async def disable_LLM(sid):
            self.llmWrapper.API.set_LLM_status(False)

        @sio.event
        async def enable_LLM(sid):
            self.llmWrapper.API.set_LLM_status(True)

        @sio.event
        async def disable_TTS(sid):
            self.tts.API.set_TTS_status(False)

        @sio.event
        async def enable_TTS(sid):
            self.tts.API.set_TTS_status(True)

        @sio.event
        async def disable_STT(sid):
            self.stt.API.set_STT_status(False)

        @sio.event
        async def enable_STT(sid):
            self.stt.API.set_STT_status(True)

        @sio.event
        async def disable_movement(sid):
            print("Disable Movement: Not implemented")

        @sio.event
        async def enable_movement(sid):
            print("Enable Movement: Not implemented")

        @sio.event
        async def disable_twitch(sid):
            self.twitchClient.API.set_twitch_status(False)

        @sio.event
        async def enable_twitch(sid):
            self.twitchClient.API.set_twitch_status(True)

        @sio.event
        async def cancel_next_message(sid):
            self.llmWrapper.API.cancel_next()

        @sio.event
        async def abort_current_message(sid):
            self.tts.API.abort_current()

        # When a new client connects, send them the status of everything
        @sio.event
        async def connect(sid, environ):
            # Set signals to themselves to trigger setter function and the sio.emit
            self.signals.AI_thinking = self.signals.AI_thinking
            self.signals.AI_speaking = self.signals.AI_speaking
            self.signals.human_speaking = self.signals.human_speaking
            self.signals.recentTwitchMessages = self.signals.recentTwitchMessages
            await sio.emit("patience_update", {"crr_time": time.time() - self.signals.last_message_time, "total_time": PATIENCE})
            await sio.emit('twitch_status', self.twitchClient.API.get_twitch_status())
            # Collect the enabled status of the llm, tts, stt, and movement and send it to the client
            await sio.emit('LLM_status', self.llmWrapper.API.get_LLM_status())
            await sio.emit('TTS_status', self.tts.API.get_TTS_status())
            await sio.emit('STT_status', self.stt.API.get_STT_status())
            await sio.emit('movement_status', False) # TODO: Not Implemented

        @sio.event
        def disconnect(sid):
            print('Client disconnected')

        async def send_messages():
            while True:
                while not self.signals.sio_queue.empty():
                    event, data = self.signals.sio_queue.get()
                    #print(f"Sending {event} with {data}")
                    await sio.emit(event, data)
                await sio.sleep(0.1)

        async def init_app():
            sio.start_background_task(send_messages)
            return app

        web.run_app(init_app())
