"""
This is a echo bot.
It echoes any incoming text messages.
"""

import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.executor import start_webhook

BOT_TOKEN = os.environ['BOT_TOKEN']

# webhook settings
WEBHOOK_HOST = os.environ['WEBHOOK_HOST_ADDR']
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = '0.0.0.0'  # or ip
WEBAPP_PORT = os.environ['PORT']

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


@dp.message_handler(regexp='(^cat[s]?$|puss)')
async def cats(message: types.Message):
    with open('data/cats.jpg', 'rb') as photo:
        '''
        # Old fashioned way:
        await bot.send_photo(
            message.chat.id,
            photo,
            caption='Cats are here 😺',
            reply_to_message_id=message.message_id,
        )
        '''

        await message.reply_photo(photo, caption='Cats are here 😺')


@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)

    await message.answer(message.text)


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Start webhook..\tWEBAPP_HOST-{WEBAPP_HOST}; WEBAPP_PORT-{WEBAPP_PORT};\n"
                 f"WEBAPP_URL-{WEBHOOK_URL};")


async def on_shutdown(dp):
    logging.warning('Shutting down..')
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning('Bye!')


if __name__ == '__main__':

    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
