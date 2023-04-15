import logging
from config import BOT_TOKEN_TG as BOT_TOKEN
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, ConversationHandler, CommandHandler, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

START = 1
desc_first, desc_second, desc_third, desc_fourth = ['Зал искусства Древнего Востока - этот зал '
                                                    'музея поражает своими экспонатами, представляющими разнообразные культуры и периоды Древнего Востока. Здесь можно увидеть изысканные изделия из фаянса, глины, кости, бронзы и золота, а также узнать об истории керамики, металлургии и других ремеслах в Древней Восточной цивилизации.',
                                                    'Зал естественной истории - это место, где посетители могут познакомиться с богатым миром животных, растительности и минералов нашей планеты. Здесь вы найдете различные экспонаты, такие как огромные скелеты динозавров, интерактивные показы о жизни отдельных видов животных, а также образцы различных минералов и горных пород.',
                                                    'Зал современного искусства - место, где можно ознакомиться с работами современных художников и скульпторов. В зале представлены десятки замечательных работ, каждой из которых уделяется много внимания и времени. Сюда часто приходят как профессиональные художники и дизайнеры, так и любители современного искусства.',
                                                    'Зал истории музыкальных инструментов - этот зал музея представляет удивительную коллекцию '
                                                    'музыкальных инструментов разных эпох и культур. Здесь вы сможете узнать о секретах создания каждого из огромного количества инструментов, представленных в зале, а также послушать звук каждого из них в специально оборудованной зоне. Этот зал - идеальное место для поклонников музыки всех жанров и возрастов.']


async def choose_hall(update: Update, context):
    msg = update.message.text
    if msg == 'Пойти в первый зал':
        await first_hall(update)
    if msg == 'Пойти во второй зал':
        await second_hall(update)
    if msg == 'Пойти в третий зал':
        await third_hall(update)
    if msg == 'Пойти в четвертый зал':
        await fourth_hall(update)
    if msg == 'Пойти на выход':
        await end(update)


async def start(update: Update, context):
    keyboard = ReplyKeyboardMarkup([['Пойти на выход', 'Пойти в первый зал']],
                                   one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        'Добро пожаловать! Пожалуйста, сдайте верхнюю одежду в гардероб!',
        reply_markup=keyboard)
    return START


async def first_hall(update: Update):
    keyboard = ReplyKeyboardMarkup([['Пойти во второй зал', 'Пойти на выход']],
                                   resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(desc_first, reply_markup=keyboard)


async def second_hall(update: Update):
    keyboard = ReplyKeyboardMarkup([['Пойти в третий зал']],
                                   resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(desc_second, reply_markup=keyboard)


async def third_hall(update: Update):
    keyboard = ReplyKeyboardMarkup([['Пойти в четвертый зал', 'Пойти в первый зал']],
                                   resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(desc_third, reply_markup=keyboard)


async def fourth_hall(update: Update):
    keyboard = ReplyKeyboardMarkup([['Пойти на выход']],
                                   resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(desc_fourth, reply_markup=keyboard)


async def end(update: Update):
    await update.message.reply_text(
        'Всего доброго, не забудьте забрать верхнюю одежду в гардеробе!')
    return ConversationHandler.END


if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            START: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_hall)]
        },
        fallbacks=[CommandHandler('exit', end)]
    )

    app.add_handler(conv_handler)

    app.run_polling()
