import os
from dotenv import load_dotenv
import discord
from modules.module import Module
from streamingSink import StreamingSink


class DiscordClient(Module):
    def __init__(self, signals, stt, enabled=True):
        super().__init__(signals, enabled)

        self.stt = stt

    async def run(self):
        bot = discord.Bot()
        connections = {}

        @bot.event
        async def on_ready():
            print(f"{bot.user} is online.")

        @bot.slash_command(name="ping", description="Check the bot's status")
        async def ping(ctx):
            await ctx.respond(f"Pong! {bot.latency}")

        async def finished_callback(sink, channel: discord.TextChannel, *args):
            await sink.vc.disconnect()
            await channel.send("Finished!")

        @bot.slash_command(name="start", description="Bot will join your vc")
        async def start(ctx: discord.ApplicationContext):
            """Record your voice!"""
            voice = ctx.author.voice

            if not voice:
                return await ctx.respond("You're not in a vc right now")

            vc = await voice.channel.connect()
            connections.update({ctx.guild.id: vc})

            vc.start_recording(
                StreamingSink(self.signals, self.stt),
                finished_callback,
                ctx.channel,
            )

            await ctx.respond("The recording has started!")

        @bot.slash_command(name="stop", description="Bot will exit the vc")
        async def stop(ctx: discord.ApplicationContext):
            """Stop recording."""
            if ctx.guild.id in connections:
                vc = connections[ctx.guild.id]
                vc.stop_recording()
                del connections[ctx.guild.id]
                await ctx.delete()
            else:
                await ctx.respond("Not recording in this guild.")

        load_dotenv()
        bot.run(os.getenv('DISCORD_TOKEN'))
