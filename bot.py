import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiosmtplib import send
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

from config import TOKEN, smtp_user, smtp_password

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def send_email(subject, body, attachments=None):
    message = MIMEMultipart()
    message['From'] = smtp_user
    message['To'] = smtp_user  
    message['Subject'] = subject

    message.attach(MIMEText(body, 'plain'))

    if attachments:
        for file_path, file_type in attachments:
            part = MIMEBase('application', 'octet-stream')
            try:
                with open(file_path, 'rb') as file:
                    part.set_payload(file.read())
            except Exception as e:
                logging.error(f"Ошибка при загрузке файла {file_path}: {e}")
                continue

            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
            message.attach(part)

    try:
        await send(
            message, 
            hostname="smtp.gmail.com", 
            port=587, 
            username=smtp_user, 
            password=smtp_password, 
            start_tls=True
        )
        logging.info("Email отправлен успешно.")
    except Exception as e:
        logging.error(f"Ошибка при отправке email: {e}")


@dp.message(Command('start'))
async def start(message: types.Message):
    await message.answer(
        "👋 Привет! Я помогу отправить тебе сообщения на почту! Выбери, что ты хочешь отправить:\n"
        "/send_message - отправить сообщение\n"
        "/send_photo - отправить фото\n"
        "/send_video - отправить видео\n"
        "/send_audio - отправить аудио"
    )


@dp.message(Command('send_message'))
async def send_message(message: types.Message):
    await message.answer("Отправь мне текстовое сообщение, чтобы я отправил его на почту.")
    @dp.message()
    async def handle_text_message(msg: types.Message):
        subject = "Новое сообщение"
        body = msg.text
        await send_email(subject, body)
        await msg.answer("Сообщение отправлено на почту!")


@dp.message(Command('send_photo'))
async def send_photo(message: types.Message):
    await message.answer("Отправь фото, которое ты хочешь отправить на почту.")
    
    @dp.message(content_types=['photo'])
    async def handle_photo(msg: types.Message):
        file_id = msg.photo[-1].file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'
        subject = "Новое фото"
        body = "Вы прислали фото."
        attachments = [(file_url, "image/jpeg")]
        await send_email(subject, body, attachments=attachments)
        await msg.answer("Фото отправлено на почту!")


@dp.message(Command('send_video'))
async def send_video(message: types.Message):
    await message.answer("Отправь видео, которое ты хочешь отправить на почту.")
    
    @dp.message(content_types=['video'])
    async def handle_video(msg: types.Message):
        file_id = msg.video.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'
        subject = "Новое видео"
        body = "Вы прислали видео."
        attachments = [(file_url, "video/mp4")]
        await send_email(subject, body, attachments=attachments)
        await msg.answer("Видео отправлено на почту!")


@dp.message(Command('send_audio'))
async def send_audio(message: types.Message):
    await message.answer("Отправь аудио, которое ты хочешь отправить на почту.")
    
    @dp.message(content_types=['audio'])
    async def handle_audio(msg: types.Message):
        file_id = msg.audio.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'
        subject = "Новое аудио"
        body = "Вы прислали аудио."
        attachments = [(file_url, "audio/mpeg")]
        await send_email(subject, body, attachments=attachments)
        await msg.answer("Аудио отправлено на почту!")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
