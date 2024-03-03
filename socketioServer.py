from aiohttp import web
import socketio

class SocketIOServer:
    sio = None

    def __init__(self):
        pass

    def start_server(self, signals, history, stt, tts, llmWrapper, prompter):
        sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
        app = web.Application()
        sio.attach(app)
        self.sio = sio

        @sio.event
        async def get_blacklist(sid):
            await sio.emit('get_blacklist', llmWrapper.API.get_blacklist())

        @sio.event
        async def set_blacklist(sid, message):
            await llmWrapper.API.set_blacklist(message)


        # @sio.event
        # async def connect(sid, environ):
        #     await sio.emit('my_response', {'data': 'Connected', 'count': 0}, room=sid)
        #
        # @sio.event
        # def disconnect(sid):
        #     print('Client disconnected')

        web.run_app(app)
