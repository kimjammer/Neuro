import asyncio
import time
from aiohttp import web
import socketio
from constants import PATIENCE


class SocketIOServer:
    def __init__(self):
        self.sio = None
        self.loop = None

    def init_event_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.set_debug(True)
        self.loop.slow_callback_duration = 0.01
        self.loop.run_forever()
        print("Event loop started")

    async def midware(self, event, data):
        await self.sio.emit(event, data)

    def emit(self, event, data=None):
        print("Scheduling task", event)
        asyncio.run_coroutine_threadsafe(self.midware(event, data), self.loop)

    def start_server(self, signals, history, stt, tts, llmWrapper, prompter, twitchClient):
        sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
        # This removes the delay in the socket.io connection for whatever reason
        # sio.instrument(auth={
        #     'username': 'admin',
        #     'password': 'admin',
        # })
        app = web.Application()
        sio.attach(app)
        self.sio = sio

        @sio.event
        async def get_blacklist(sid):
            await sio.emit('get_blacklist', llmWrapper.API.get_blacklist())

        @sio.event
        async def set_blacklist(sid, message):
            await llmWrapper.API.set_blacklist(message)

        @sio.event
        async def disable_LLM(sid):
            await llmWrapper.API.set_LLM_status(False)

        @sio.event
        async def enable_LLM(sid):
            await llmWrapper.API.set_LLM_status(True)

        @sio.event
        async def disable_TTS(sid):
            await tts.API.set_TTS_status(False)

        @sio.event
        async def enable_TTS(sid):
            await tts.API.set_TTS_status(True)

        @sio.event
        async def disable_STT(sid):
            await stt.API.set_STT_status(False)

        @sio.event
        async def enable_STT(sid):
            await stt.API.set_STT_status(True)

        @sio.event
        async def disable_movement(sid):
            print("Disable Movement: Not implemented")

        @sio.event
        async def enable_movement(sid):
            print("Enable Movement: Not implemented")

        @sio.event
        async def disable_twitch(sid):
            await twitchClient.API.set_twitch_status(False)

        @sio.event
        async def enable_twitch(sid):
            await twitchClient.API.set_twitch_status(True)

        @sio.event
        async def cancel_next_message(sid):
            llmWrapper.API.cancel_next()

        @sio.event
        async def abort_current_message(sid):
            tts.API.abort_current()

        # When a new client connects, send them the status of everything
        @sio.event
        async def connect(sid, environ):
            # Set signals to themselves to trigger setter function and the sio.emit
            signals.AI_thinking = signals.AI_thinking
            signals.AI_speaking = signals.AI_speaking
            signals.human_speaking = signals.human_speaking
            signals.recentTwitchMessages = signals.recentTwitchMessages
            await sio.emit("patience_update", {"crr_time": time.time() - signals.last_message_time, "total_time": PATIENCE})
            await sio.emit('twitch_status', twitchClient.API.get_twitch_status())
            # Collect the enabled status of the llm, tts, stt, and movement and send it to the client
            await sio.emit('LLM_status', llmWrapper.API.get_LLM_status())
            await sio.emit('TTS_status', tts.API.get_TTS_status())
            await sio.emit('STT_status', stt.API.get_STT_status())
            await sio.emit('movement_status', False) # TODO: Not Implemented

        @sio.event
        def disconnect(sid):
            print('Client disconnected')

        return app