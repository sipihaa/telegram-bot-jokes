import boto3
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Настройка доступа к Object Storage
session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id='YCAJEZInm7Pu5tsMvsNmwI-bW',
    aws_secret_access_key='YCP7wsGzDoMG1MRy_3me3YbnvMzdwp-obkGIVaAy'
)

BUCKET_NAME = 'facts-jokes-for-tg-bot'

def get_random_line_from_file(filename):
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=filename)
    lines = obj['Body'].read().decode('utf-8').split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    return random.choice(lines)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я Бот Настроения.\nКоманды:\n/fact — интересный факт\n/joke — анекдот")

async def fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fact = get_random_line_from_file('facts.txt')
    await update.message.reply_text(f"🧠 Факт: {fact}")

async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joke = get_random_line_from_file('jokes.txt')
    await update.message.reply_text(f"😂 Анекдот: {joke}")

if __name__ == '__main__':
    application = ApplicationBuilder().token("8076838273:AAEezwxmb67RDQ8hDLVCRZEKBQLPagEBD_E").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("fact", fact))
    application.add_handler(CommandHandler("joke", joke))

    application.run_polling()
