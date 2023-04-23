import logging
import os.path

import requests

from config import BOT_TOKEN_TG as BOT_TOKEN
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, ConversationHandler, CommandHandler, MessageHandler, \
    filters, ContextTypes
from telegram import Bot
import json

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Здравствуйте. Введите координаты (через запятую) или название искомого топонима')


def geo(toponym):
    params = {
        'geocode': toponym,
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        'format': 'json'
    }
    r = requests.get(url='https://geocode-maps.yandex.ru/1.x', params=params)
    if r.status_code != 200:
        return False
    try:
        if not r.json()["response"]["GeoObjectCollection"]["featureMember"][0]:
            return False
    except Exception:
        return False
    return r.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"][
        'pos'].split()


def maps(toponym, name, z=20):
    if not toponym:
        return False
    params = {
        'l': 'map',
        'll': ','.join(toponym),
        'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
        'pt': f'{toponym[0]},{toponym[1]},pmwtm50',
        'z': z
    }
    r = requests.get(url='https://static-maps.yandex.ru/1.x/', params=params)
    print(r)
    with open(f"{name}.png", 'wb') as f:
        f.write(r.content)


async def geo_(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    if all(msg.split(',')) and len(msg.split(',')) == 2:
        toponym = msg.split(',')
        maps(toponym, f'map_{update.effective_user.id}_')
    else:
        maps(geo(msg), f'map_{update.effective_user.id}_', z=10)
    if not os.path.exists(f'map_{update.effective_user.id}_.png'):
        await update.message.reply_text('Ничего не найдено')
        return
    await update.message.reply_photo(f'map_{update.effective_user.id}_.png',
                                     caption=f'Карта по запросу {msg}')


if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN).build()
    bot = Bot(BOT_TOKEN)

    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, geo_))

    app.run_polling()
