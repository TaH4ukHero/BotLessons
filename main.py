import asyncio
import requests
from discord.ext import commands
import discord
import logging
from config import *

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

TOKEN = BOT_TOKEN_DISCORD  # вставь свой токен

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)


def translate(text, target, source):
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "application/gzip",
        "X-RapidAPI-Key": RapidApiKey,
        "X-RapidAPI-Host": "google-translate1.p.rapidapi.com"
    }
    url = "https://google-translate1.p.rapidapi.com/language/translate/v2"
    params = {
        'q': text,
        'target': target,
        'source': source
    }
    r = requests.request("POST", url, data=params, headers=headers).json()
    return r["data"]['translations'][0]["translatedText"]


class BotTranslate(commands.Cog):
    def __int__(self, bot):
        self.bot = bot
        # Я не понимаю почему при инициалазации он не видит эти переменные
        self.source, self.target = 'en', 'ru'

    @commands.command(name='help_bot')
    async def help(self, ctx):
        await ctx.send('"!set_lang" - смена направления перевода в формате "с какого"-"на какой"'
                       'по стандарту "en-ru"\n"!text" - ввод слова для перевода')

    @commands.command(name='set_lang')
    async def set_lang(self, ctx, direction: str):
        self.source, self.target = direction.split('-')
        await ctx.send(f'Курс поменян. Текущий - {self.source}-{self.target}')

    @commands.command(name='text')
    async def text(self, ctx, word):
        await ctx.send(translate(word, self.target, self.source))


async def main():
    cog = BotTranslate(bot)
    await bot.add_cog(cog)
    await bot.start(TOKEN)


asyncio.run(main())
