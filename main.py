import logging
import random
from config import BOT_TOKEN_TG as BOT_TOKEN
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, ConversationHandler, CommandHandler, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

START, DICE, TIMER = range(3)


async def start(update: Update, context):
    keyboard = ReplyKeyboardMarkup([['/dice', '/timer']], one_time_keyboard=True,
                                   resize_keyboard=True)
    await update.message.reply_text("Выберите команду",
                                    reply_markup=keyboard)
    return START


async def choose_mode(update: Update, context):
    msg = update.message.text
    if msg == '/dice':
        keyboard = ReplyKeyboardMarkup(
            [["кинуть один шестигранный кубик", "кинуть 2 шестигранных кубика одновременно"],
             ["кинуть 20-гранный кубик", "вернуться назад"]], resize_keyboard=True)
        await update.message.reply_text('Выберите один из пунктов', reply_markup=keyboard)
        return DICE
    elif msg == '/timer':
        keyboard = ReplyKeyboardMarkup([["30 секунд", "1 минута"],
                                        ["5 минут", "вернуться назад"]], resize_keyboard=True,
                                       one_time_keyboard=True)
        await update.message.reply_text('Выберите один из пунктов', reply_markup=keyboard)
        return TIMER


async def dice_throw(update: Update, context):
    msg = update.message.text
    if msg == "кинуть один шестигранный кубик":
        await update.message.reply_text(f"{random.randint(1, 6)}")
    elif msg == "кинуть 2 шестигранных кубика одновременно":
        await update.message.reply_text(f"{random.randint(1, 6)}, {random.randint(1, 6)}")
    elif msg == "кинуть 20-гранный кубик":
        await update.message.reply_text(f"{random.randint(1, 20)}")
    elif msg == "вернуться назад":
        keyboard = ReplyKeyboardMarkup([['/dice', '/timer']], one_time_keyboard=True,
                                       resize_keyboard=True)
        await update.message.reply_text('Возвращение', reply_markup=keyboard)
        return START


async def task(context):
    due = context.job.data
    await context.bot.send_message(context.job.chat_id,
                text=f'{due // 60 if due >= 60 else due} {"м." if due // 60 >= 1 else "с."} истекло',
                reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def remove_job_if_exists(name, context):
    """Удаляем задачу по имени.
    Возвращаем True если задача была успешно удалена."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


# Обычный обработчик, как и те, которыми мы пользовались раньше.
async def set_timer(update, context, due):
    """Добавляем задачу в очередь"""
    chat_id = update.effective_message.chat_id
    # Добавляем задачу в очередь
    # и останавливаем предыдущую (если она была)
    context.user_data["due"] = due
    context.job_queue.run_once(task, due, chat_id=chat_id, name=str(chat_id), data=due)

    text = f'Засек {due // 60 if due >= 60 else due} {"м" if due // 60 >= 1 else "с"}.!'
    await update.effective_message.reply_text(text)


async def unset(update, context):
    """Удаляет задачу, если пользователь передумал"""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Таймер отменен!' if job_removed else 'У вас нет активных таймеров'
    await update.message.reply_text(text)


async def timer(update: Update, context):
    msg = update.message.text
    if msg == "30 секунд":
        await set_timer(update, context, 30)
    elif msg == "1 минута":
        await set_timer(update, context, 60)
    elif msg == "5 минут":
        await set_timer(update, context, 300)
    elif msg == "вернуться назад":
        keyboard = ReplyKeyboardMarkup([['/dice', '/timer']], one_time_keyboard=True,
                                       resize_keyboard=True)
        await update.message.reply_text('Возвращение', reply_markup=keyboard)
        return START
    keyboard = ReplyKeyboardMarkup([['/close']], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text('Отмена таймера', reply_markup=keyboard)


async def stop(update: Update, context):
    await update.message.reply_text('ГГ  Я ЛИВАЮ ТИМА РАКОВ')
    return ConversationHandler.END


if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            START: [MessageHandler(filters.TEXT & filters.COMMAND, choose_mode)],
            DICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, dice_throw)],
            TIMER: [MessageHandler(filters.TEXT & ~filters.COMMAND, timer),
                    CommandHandler('close', unset)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    app.add_handler(conv_handler)
    app.run_polling()
