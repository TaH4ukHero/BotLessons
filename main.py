import asyncio

import discord
import logging

import requests

from config import *

logger = logging.getLogger('http.discord')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

TOKEN = BOT_TOKEN_DISCORD  # вставь свой токен


class YLBotClient(discord.Client):
    async def on_ready(self):
        logger.info(f'{self.user} has connected to Discord!')
        for guild in self.guilds:
            logger.info(
                f'{self.user} подключились к чату:\n'
                f'{guild.name}(id: {guild.id})')

    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(
            f'Привет, {member.name}!'
        )

    async def on_message(self, message: discord.Message):
        if 'set_timer' in message.content.lower():
            msg = message.content.lower()
            hours, minutes = int(msg.split()[2]), int(msg.split()[4])
            due = hours * 3600 + minutes * 60
            await message.channel.send(f'The timer should start in {hours} hours and {minutes} '
                                       f'minutes.')
            await asyncio.sleep(due)
            await message.channel.send('Time X has come')


intents = discord.Intents.all()
client = YLBotClient(intents=intents)
client.run(TOKEN)
