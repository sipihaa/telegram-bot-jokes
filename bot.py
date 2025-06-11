import boto3
import random
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# Настройка доступа к Object Storage
session = boto3.session.Session()  
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id='YCAJEZInm7Pu5tsMvsNmwI-bW',
    aws_secret_access_key='YCP7wsGzDoMG1MRy_3me3YbnvMzdwp-obkGIVaAy'
)

BUCKET_NAME = 'facts-jokes-for-tg-bot'

def get_random_fact_from_file(filename):
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=filename)
    lines = obj['Body'].read().decode('utf-8').split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    return random.choice(lines)


def get_random_joke_from_file(filename):
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=filename)
    text = obj['Body'].read().decode('utf-8')
    jokes = [joke.strip() for joke in re.split(r'\n\s*\n\s*\n+', text) if joke.strip()]
    jokes = [joke for joke in jokes if not joke.isdigit()]
    return random.choice(jokes)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🧠 Расскажи интересный факт", callback_data='fact')],
        [InlineKeyboardButton("😂 Расскажи анекдот", callback_data='joke')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Привет! Я Бот Настроения.\nКоманды:\n/fact — интересный факт\n/joke — анекдот",
                                    reply_markup=reply_markup)


# Эта функция будет вызываться при нажатии на любую инлайн-кнопку
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    # Обязательно "отвечаем" на колбэк, чтобы у пользователя пропали "часики" на кнопке
    await query.answer()

    # Получаем данные, которые мы задали в callback_data
    callback_data = query.data

    # В зависимости от данных вызываем нужную функцию
    if callback_data == 'fact':
        await fact(query, context)
    elif callback_data == 'joke':
        await joke(query, context)
    else:
        await query.edit_message_text(text=f"Неизвестный колбэк: {callback_data}")

async def fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fact = get_random_fact_from_file('facts.txt')  
    await update.message.reply_text(f"🧠 Факт: {fact}")


async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joke = get_random_joke_from_file('jokes.txt')
    await update.message.reply_text(f"😂 Анекдот:\n{joke}")


if __name__ == '__main__':
    application = ApplicationBuilder().token("8076838273:AAEezwxmb67RDQ8hDLVCRZEKBQLPagEBD_E").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("fact", fact))
    application.add_handler(CommandHandler("joke", joke))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling()
