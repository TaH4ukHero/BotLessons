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
        if 'кот' in message.content.lower():
            r = requests.get('https://api.thecatapi.com/v1/images/search').json()[0]
            logger.info(r)
            await message.channel.send(r["url"])
        elif 'собак' in message.content.lower():
            r = requests.get('https://dog.ceo/api/breeds/image/random').json()
            await message.channel.send(r["message"])


intents = discord.Intents.all()
client = YLBotClient(intents=intents)
client.run(TOKEN)
