import logging
from config import BOT_TOKEN_TG as BOT_TOKEN
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, ConversationHandler, CommandHandler, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

poem = """Последняя туча рассеянной бури!
Одна ты несешься по ясной лазури,
Одна ты наводишь унылую тень,
Одна ты печалишь ликующий день.
Ты небо недавно кругом облегала,
И молния грозно тебя обвивала;
И ты издавала таинственный гром
И алчную землю поила дождем.
Довольно, сокройся! Пора миновалась,
Земля освежилась, и буря промчалась,
И ветер, лаская листочки древес,
Тебя с успокоенных гонит небес.""".split('\n')


async def start(update: Update, context):
    context.user_data["number"] = 1
    await update.message.reply_text(poem[0])
    return 1


async def suphler(update, context):
    await update.message.reply_text(f'Нет не так\nСледующая строка начинается с\n'
                                    f'{poem[context.user_data["number"]][:10]}...')


async def handler(update: Update, context):
    msg = update.message.text
    if context.user_data["number"] == len(poem):
        print(context.user_data["number"], str(len(poem)), poem)
        await update.message.reply_text('Я рад что ты смог! Не хочешь повторить?')
        return ConversationHandler.END
    if msg == poem[context.user_data["number"]]:
        context.user_data["number"] += 2
        if context.user_data["number"] >= len(poem):
            await update.message.reply_text('Я рад что ты смог! Не хочешь повторить?')
            return ConversationHandler.END
        await update.message.reply_text(
            poem[context.user_data["number"] - 1])
        return
    await suphler(update, context)


async def stop(update: Update, context):
    await update.message.reply_text('Конечная')
    return ConversationHandler.END


if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, handler),
                CommandHandler('suphler', suphler)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    app.add_handler(conv_handler)

    app.run_polling()
