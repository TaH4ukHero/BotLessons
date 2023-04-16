import logging
from config import BOT_TOKEN_TG as BOT_TOKEN
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, ConversationHandler, CommandHandler, MessageHandler, filters
from telegram import Bot
import json

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

bot = Bot(BOT_TOKEN)


def results(context):
    context = context.user_data
    n = context["n_of_tests"]
    correct = context["correct_answers"]
    return f"Всего вопросов было - {n if n < 10 else 10}\nПравильно отвеченные - " \
           f"{correct}"


async def get_tests(update: Update, context):
    document = update.message.document
    file = await bot.get_file(document.file_id)
    await file.download_to_drive('data/tests.json')
    with open('data/tests.json', encoding='utf8') as f:
        tests = json.load(f)
        context.user_data["tests"] = tests["test"]
        context.user_data["n_of_tests"] = len(tests["test"])


async def start(update: Update, context):
    context.user_data["curr_question"] = context.user_data['tests'].pop()
    context.user_data["correct_answers"] = 0
    context.user_data["answered_questions"] = 0
    await update.message.reply_text('Не желаете ли Вы пройти тест по всеобщим знаниям?\nПервый '
                                    f'вопрос\n'
                                    f'{context.user_data["curr_question"]["question"]}')
    return 1


async def get_answer(update: Update, context):
    msg = update.message.text
    if msg == context.user_data["curr_question"]["response"]:
        await update.message.reply_text('Правильно!')
        context.user_data["correct_answers"] += 1
    else:
        await update.message.reply_text('К сожалению неправильно(')
    context.user_data["answered_questions"] += 1
    if not context.user_data["tests"] or context.user_data["answered_questions"] == 10:
        await update.message.reply_text('Все вопросы закончились. Подвожу итоги...')
        await update.message.reply_text(results(context))
        return
    await update.message.reply_text('Следующий вопрос!')
    context.user_data["curr_question"] = context.user_data['tests'].pop()
    await update.message.reply_text(context.user_data["curr_question"]["question"])


async def stop(update: Update, context):
    await update.message.reply_text('Конечная')
    return ConversationHandler.END


if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_answer)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.Document.ALL, get_tests))

    app.run_polling()
