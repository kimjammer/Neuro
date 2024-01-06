from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
import os
from dotenv import load_dotenv


class TwitchClient:
    signals = None
    chat = None
    twitch = None

    def __init__(self, signals):
        self.signals = signals

    async def shutdown(self):
        self.chat.stop()
        await self.twitch.close()

    async def start_twitch_bot(self):
        load_dotenv()
        APP_ID = os.getenv("TWITCH_APP_ID")
        APP_SECRET = os.getenv("TWITCH_SECRET")
        USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]
        TARGET_CHANNEL = 'lunasparkai'

        # this will be called when the event READY is triggered, which will be on bot start
        async def on_ready(ready_event: EventData):
            print('TWITCH: Bot is ready for work, joining channels')
            # join our target channel, if you want to join multiple, either call join for each individually
            # or even better pass a list of channels as the argument
            await ready_event.chat.join_room(TARGET_CHANNEL)
            # you can do other bot initialization things in here

        # this will be called whenever a message in a channel was send by either the bot OR another user
        async def on_message(msg: ChatMessage):
            print(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')
            # Store the 10 most recent chat messages
            if len(self.signals.recentTwitchMessages) > 10:
                self.signals.recentTwitchMessages.pop(0)
            self.signals.recentTwitchMessages.append(f"{msg.user.name} : {msg.text}")

        # this will be called whenever someone subscribes to a channel
        async def on_sub(sub: ChatSub):
            print(f'New subscription in {sub.room.name}:\\n'
                  f'  Type: {sub.sub_plan}\\n'
                  f'  Message: {sub.sub_message}')

        # this will be called whenever the !reply command is issued
        async def test_command(cmd: ChatCommand):
            if len(cmd.parameter) == 0:
                await cmd.reply('you did not tell me what to reply with')
            else:
                await cmd.reply(f'{cmd.user.name}: {cmd.parameter}')

        # set up twitch api instance and add user authentication with some scopes
        twitch = await Twitch(APP_ID, APP_SECRET)
        auth = UserAuthenticator(twitch, USER_SCOPE)
        token, refresh_token = await auth.authenticate()
        await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

        # create chat instance
        chat = await Chat(twitch)

        # also save twitch and chat to class properties so we can shut them down
        self.twitch = twitch
        self.chat = chat

        # register the handlers for the events you want

        # listen to when the bot is done starting up and ready to join channels
        chat.register_event(ChatEvent.READY, on_ready)
        # listen to chat messages
        chat.register_event(ChatEvent.MESSAGE, on_message)
        # listen to channel subscriptions
        chat.register_event(ChatEvent.SUB, on_sub)
        # there are more events, you can view them all in this documentation

        # you can directly register commands and their handlers, this will register the !reply command
        chat.register_command('reply', test_command)

        # we are done with our setup, lets start this bot up!
        chat.start()
