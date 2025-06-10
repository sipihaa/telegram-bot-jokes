import random
import boto3
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from yandexcloud import SDK  # для работы с Lockbox

# ID секрета Lockbox (скопируй его из консоли Yandex Cloud)
SECRET_ID = 'e6qdpuv6kan6vgr4qdcv'
BUCKET_NAME = 'facts-jokes-for-tg-bot'
ENDPOINT = 'https://storage.yandexcloud.net'


def get_secrets_from_lockbox(secret_id: str):
    sdk = SDK()  # Автоматически использует IAM-сервисный аккаунт внутри ВМ
    client = sdk.client('lockbox_payload')
    response = client.get_payload(secret_id=secret_id)

    access_key = None
    secret_key = None

    for entry in response.entries:
        if entry.key == 'access_key':
            access_key = entry.text_value
        elif entry.key == 'secret_key':
            secret_key = entry.text_value

    if not access_key or not secret_key:
        raise ValueError("Ключи доступа не найдены в Lockbox")

    return access_key, secret_key


def get_random_line_from_s3(s3, filename):
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=filename)
    lines = obj['Body'].read().decode('utf-8').split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    return random.choice(lines)


# Обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я Бот Настроения 🤖\n"
        "Команды:\n"
        "/fact — интересный факт\n"
        "/joke — анекдот"
    )


async def fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fact = get_random_line_from_s3(context.bot_data['s3'], 'facts.txt')
    await update.message.reply_text(f"🧠 Факт: {fact}")


async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joke = get_random_line_from_s3(context.bot_data['s3'], 'jokes.txt')
    await update.message.reply_text(f"😂 Анекдот: {joke}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # Получаем ключи из Lockbox
    access_key, secret_key = get_secrets_from_lockbox(SECRET_ID)

    # Создаём клиента для Yandex Object Storage
    s3 = boto3.client(
        service_name='s3',
        endpoint_url=ENDPOINT,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    # Получаем Telegram-токен из переменной окружения
    import os
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    if not TELEGRAM_TOKEN:
        raise RuntimeError("Переменная TELEGRAM_TOKEN не задана")

    # Инициализация Telegram-бота
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Передаём объект s3 во все хендлеры через context.bot_data
    app.bot_data['s3'] = s3

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("fact", fact))
    app.add_handler(CommandHandler("joke", joke))

    logging.info("Бот запущен...")
    app.run_polling()
