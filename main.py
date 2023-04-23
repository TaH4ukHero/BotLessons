import logging
import os.path

import requests

from config import *
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, ConversationHandler, CommandHandler, MessageHandler, \
    filters, ContextTypes
from telegram import Bot
import json

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

DIALOG = 1


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Здравствуйте, я бот-переводчик. Введите слово и я его переведу'
                                    '\nСейчас перевод с руского на английский язык')
    context.user_data["target"] = 'en'
    return DIALOG


def translate(text, target):
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
        'source': ''
    }
    if target == 'en':
        params["source"] = 'ru'
        r = requests.request("POST", url, data=params, headers=headers).json()
    else:
        params["source"] = 'en'
        r = requests.request("POST", url, data=params, headers=headers).json()
    return r["data"]['translations'][0]["translatedText"]


async def reply_translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup([['Переводить с русского на английский'],
                                    ['Переводить с английского на русский']], resize_keyboard=True)
    if 'Переводить с русского на английский' == update.message.text:
        context.user_data["target"] = 'en'
        await update.message.reply_text('Курс поменян')
    elif 'Переводить с английского на русский' == update.message.text:
        context.user_data["target"] = 'ru'
        await update.message.reply_text('Курс поменян')
    else:
        text = translate(update.message.text, context.user_data["target"])
        if text == update.message.text:
            await update.message.reply_text('Перевод не удался. Проверьте правильность ввода')
            return
        await update.message.reply_html(f"Перевод завершен\nРезультат - <b>{text}</b>",
                                        reply_markup=keyboard)


async def stop(update, context):
    await update.message.reply_text('Завершение работы...')


if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN_TG).build()
    bot = Bot(BOT_TOKEN_TG)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            DIALOG: [MessageHandler(filters.TEXT & ~filters.COMMAND, reply_translate)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    app.add_handler(conv_handler)

    app.run_polling()
