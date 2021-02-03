import logging
import gc
import os
import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils.executor import start_webhook
from network_test import *  # Import architecture
from help_functions import *  # Import help functions


# Set API_TOKEN. You must have your own.


BOT_TOKEN = os.environ['BOT_TOKEN']

# webhook settings
WEBHOOK_HOST = os.environ['WEBHOOK_HOST_ADDR']
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = '0.0.0.0'  # or ip
WEBAPP_PORT = os.environ['PORT']

# Configure logging.
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher.
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Initialize the net.
style_model = Net(ngf=128)
style_model.load_state_dict(torch.load('pretrained.model'), False)

# Initializing flags to check for images.
content_flag = False
style_flag = False


class GetPictures(StatesGroup):
    waiting_for_photos = State()
    waiting_for_another_photos = State()


class GetCity(StatesGroup):
    waiting_for_city = State()


buttons_for_start = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
buttons_for_start.add(types.KeyboardButton(text="I want to start style transfer \U0000270D"))
buttons_for_start.add(types.KeyboardButton(text="What can you do? \U0001F9D0"))
buttons_for_start.add(types.KeyboardButton(text="I want to have some interesting examples of style \U0001F30C"))
buttons_for_start.add(types.KeyboardButton(text="Tell me about your creator \U0001F468\U0000200D\U0001F4BB"))
buttons_for_start.add(types.KeyboardButton(text="What is the weather now? \U00002600"))

buttons_for_content = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
buttons_for_content.add(types.KeyboardButton(text="I want another content image \U0001F501"))

buttons_for_style = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
buttons_for_style.add(types.KeyboardButton(text="Let's start style transfer \U0001F3C1"))
buttons_for_style.add(types.KeyboardButton(text="I want another style image \U0001F501"))



def transform(content_root, style_root, im_size):
    """Function for image transformation."""
    content_image = tensor_load_rgbimage(content_root, size=im_size,
                                         keep_asp=True).unsqueeze(0)
    style = tensor_load_rgbimage(style_root, size=im_size).unsqueeze(0)
    style = preprocess_batch(style)
    style_v = Variable(style)
    content_image = Variable(preprocess_batch(content_image))
    style_model.setTarget(style_v)
    output = style_model(content_image)
    tensor_save_bgrimage(output.data[0], 'result' + user_id + '.jpg', False)

    # Clear the RAM.
    del content_image
    del style
    del style_v
    del output
    torch.cuda.empty_cache()
    gc.collect()


@dp.message_handler(commands=['start'], state='*')
async def satrt(message: types.Message):
    """Test function."""
    global user_name
    user_name = str(message.from_user.first_name)
    await message.answer(text=f"Hi, *{user_name}*, \nI am very smart bot \U0001F913, what can I do for you?",
                         reply_markup=buttons_for_start, parse_mode='Markdown')


@dp.message_handler(lambda message: message.text == "Tell me about your creator \U0001F468\U0000200D\U0001F4BB",
                    state='*')
@dp.message_handler(commands=['creator'], state='*')
async def creator(message: types.Message):
    """Displays information about the bot's Creator."""

    await message.answer(text="I'm student of Deep Learning School (by MIPT) and also Data Analytics School (by X5 Retail Group). Work in PwC (Data analyst)"
    "and in 'School of programmers' (Teacher)\n\nLink to GitHub \U0001F4BB: https://github.com/PsychoBel\nContact with me \U0001F4EB: @psycho1388", reply_markup=buttons_for_start)


@dp.message_handler(commands="set_commands", state='*')
async def cmd_set_commands(message: types.Message):
    if message.from_user.id == 267917903:
        commands = [types.BotCommand(command="/transfer", description="Initialize style transfer"),
                    types.BotCommand(command="/help", description="Description of me"),
                    types.BotCommand(command="/creator", description="Information about my creator"),
                    types.BotCommand(command="/styles", description="Different interesting examples of styles"),
                    types.BotCommand(command="/weather", description="Find out the weather in your city"),
                    types.BotCommand(command="/back", description="Change picture"),
                    types.BotCommand(command="/initialize", description="Start transfer")]
        await bot.set_my_commands(commands)
        await message.answer("Команды настроены.")


@dp.message_handler(lambda message: message.text == "I want to have some interesting examples of style \U0001F30C", state='*')
@dp.message_handler(commands="styles", state='*')
async def send_different_styles(message: types.Message):
    media = types.MediaGroup()
    media.attach_photo(types.InputFile('photos_for_style/style_2'))
    media.attach_photo(types.InputFile('photos_for_style/style_3'))
    media.attach_photo(types.InputFile('photos_for_style/style_4'))
    media.attach_photo(types.InputFile('photos_for_style/style_5'))
    media.attach_photo(types.InputFile('photos_for_style/style_6'))
    media.attach_photo(types.InputFile('photos_for_style/style_7'))
    media.attach_photo(types.InputFile('photos_for_style/style_9'))
    media.attach_photo(types.InputFile('photos_for_style/style_10'))
    media.attach_photo(types.InputFile('photos_for_style/style_12'))
    media.attach_photo(types.InputFile('photos_for_style/style_13'))
    await message.reply_media_group(media=media)


@dp.message_handler(lambda message: message.text == 'What is the weather now? \U00002600', state='*')
@dp.message_handler(commands=['weather'], state='*')
async def find_city(message: types.Message):
    buttons_for_city = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons_for_city.add(types.KeyboardButton(text="Moscow"))
    buttons_for_city.add(types.KeyboardButton(text="St. Petersburg"))

    await message.answer(text="Choose in which city you would like to know the weather \U000026C5\n\n"
                              "If your city *Moscow or St. Petersburg click button below*\n\n"
                              "If you are from another city, *write it's name in English*",
                         reply_markup=buttons_for_city, parse_mode='Markdown')

    await GetCity.waiting_for_city.set()


@dp.message_handler(state=GetCity.waiting_for_city)
async def weather_in_city(message: types.Message, state: FSMContext):
    appid = 'fed49783386c49273b6565dac196d79b'
    city_id = 0
    flag = False
    if message.text == "Moscow": city_id = 524901
    elif message.text == "St. Petersburg": city_id = 4778626

    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/find",
                           params={'q': message.text, 'type': 'like', 'units': 'metric', 'APPID': appid})
        data = res.json()
        city_id = data['list'][0]['id']
    except Exception as e:
        await message.answer(text="Sorry, I couldn't find this city")
        flag = True
        await state.finish()

    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/forecast",
                           params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': appid})
        data = res.json()
        today = data['list'][0]
        await message.answer(text=f"Last update at: {today['dt_txt']}\n*Tempreture: {round(today['main']['temp'])}*\n*Condition: {today['weather'][0]['description']}*",
                             reply_markup=buttons_for_start, parse_mode='Markdown')
        await state.finish()
    except Exception as e:
        if not flag:
            await message.answer(text="Sorry, I couldn't find this city")
            await state.finish()


@dp.message_handler(lambda message: message.text == "What can you do? \U0001F9D0", state='*')
@dp.message_handler(commands=['help'], state='*')
async def help_message(message: types.Message):
    """
    Outputs a small instruction when the corresponding command is received.
    """
    await message.answer(text="This bot will helps you making style transformations \U0001FA84\n"
                              "*1) Load photo with your content first*\n"
                              "*2) Then, load photo with style*\n"
                              "*3) Choose quality of result photo*\n"
                              "*4) Get joint images and be happy!* \U0001F603\n"
                              "Let me show you some examples to make you understand:", parse_mode='Markdown')
    with open('examples/vysocz.png', 'rb') as photo:
        await message.reply_photo(photo, caption='Visocky and Van Gogh')
    with open('examples/mayak.png', 'rb') as photo:
        await message.reply_photo(photo, caption='Mayakovsky and Van Gogh')
    with open('examples/gagarin.png', 'rb') as photo:
        await message.reply_photo(photo, caption='Gagarin and Van Gogh')

    await message.answer(text='If you want to try it, *click the button below* or press */transfer*\n'
                              'Also you can read */about* my creator\nOr even find out the */weather* in your city',
                         reply_markup=buttons_for_start, parse_mode='Markdown')


@dp.message_handler(lambda message: message.text == "I want to start style transfer \U0000270D", state='*')
@dp.message_handler(commands=['transfer'], state='*')
async def start_style_transfer(message: types.Message):
    global user_id
    user_id = str(message.from_user.id)
    await message.answer(text="Let's start \U0001F4AB\n"
                              "Send me *content* image please", parse_mode='Markdown')
    await GetPictures.waiting_for_photos.set()


@dp.message_handler(state=GetPictures.waiting_for_photos, content_types=types.ContentTypes.PHOTO)
async def photo_processing(message):
    """
    Triggered when the user sends an image and saves it for further processing.
    """
    global content_flag
    global style_flag

    # The bot is waiting for a picture with content from the user.
    if not content_flag:
        await message.photo[-1].download('content' + user_id + '.jpg')
        await message.answer(text='Cool! I got content image! \U0001F525\n'
                                  '*Now, send me style image please.*\n\n'
                                  'Or click */back* command or *button below* to choose '
                                  'another content image.', reply_markup=buttons_for_content, parse_mode='Markdown')

        content_flag = True  # Now the bot knows that the content image exists.

    # The bot is waiting for a picture with style from the user.
    else:
        await message.photo[-1].download('style' + user_id + '.jpg')
        await message.answer(text='Perfect! I gor style image! \U000026A1\n'
                                  '*Now, press /initialize or *button below* to start style transfer*\n\n'
                                  'Or click */back* command or *button below* to choose '
                                  'another content image.', reply_markup=buttons_for_style, parse_mode='Markdown')

        style_flag = True

    await GetPictures.waiting_for_photos.set()


@dp.message_handler(lambda message: message.text in ("I want another style image \U0001F501",
                                                     "I want another content image \U0001F501"),
                    state=GetPictures.waiting_for_photos)
@dp.message_handler(state=GetPictures.waiting_for_photos, commands=['back'])
async def photo_processing(message: types.Message):
    """Allows the user to select a different image with content or style."""

    global content_flag
    global style_flag
    # Let's make sure that there is something to cancel.
    if content_flag and style_flag:
        await message.answer(text="Choose new style image")
        await GetPictures.waiting_for_another_photos.set()
    else:
        await message.answer(text="Choose new content image")
        await GetPictures.waiting_for_another_photos.set()


@dp.message_handler(state=GetPictures.waiting_for_another_photos, content_types=types.ContentTypes.PHOTO)
async def photo_processing(message):
    global content_flag
    global style_flag
    if content_flag and style_flag:

        await message.photo[-1].download('style' + user_id + '.jpg')
        await message.answer(text='Perfect! I gor style image! \U000026A1\n'
                                  '*Now, press /initialize or button below to start style transfer*\n\n'
                                  'Or click */back* command or *button below* to choose '
                                  'another content image.', reply_markup=buttons_for_style, parse_mode='Markdown')
        await GetPictures.waiting_for_photos.set()
    else:
        await message.photo[-1].download('content' + user_id + '.jpg')
        await message.answer(text='Cool! I got content image! \U0001F525\n'
                                  '*Now, send me style image please.*\n\n'
                                  'Or click */back* command or *button below* to choose '
                                  'another content image.', reply_markup=buttons_for_content, parse_mode='Markdown')
        await GetPictures.waiting_for_photos.set()


@dp.message_handler(lambda message: message.text == "Let's start style transfer \U0001F3C1", state=GetPictures.waiting_for_photos)
@dp.message_handler(commands=['initialize'], state=GetPictures.waiting_for_photos)
async def run_style_transfer(message: types.Message, state: FSMContext):
    """Preparing for image processing."""

    # Let's make sure that the user has added both images.
    if not (content_flag * style_flag):  # Conjunction
        await message.answer(text="Upload both images please.")
        return

    # Adding answer options.
    res = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                    one_time_keyboard=True)
    res.add(types.KeyboardButton(text="Bad quality \U0001F534, Fast processing \U0001F7E2"))
    res.add(types.KeyboardButton(text="Medium quality \U0001F7E0, Medium processing \U0001F7E0"))
    res.add(types.KeyboardButton(text="Good quality \U0001F7E2, Low processing \U0001F534"))

    await message.answer(text=" Now you need to choose the quality of the resulting photo"
                              " The better the quality of the photo you choose, the longer it will take to process the photo. ",
                         reply_markup=res)


@dp.message_handler(lambda message: message.text in ("Bad quality \U0001F534, Fast processing \U0001F7E2",
                                                     "Medium quality \U0001F7E0, Medium processing \U0001F7E0",
                                                     "Good quality \U0001F7E2, Low processing \U0001F534"),
                    state=GetPictures.waiting_for_photos)
async def processing(message: types.Message, state: FSMContext):
    """Image processing depending on the selected quality."""
    global content_flag
    global style_flag

    if message.text == 'Bad quality \U0001F534, Fast processing \U0001F7E2':
        image_size = 128
    elif message.text == 'Medium quality \U0001F7E0, Medium processing \U0001F7E0':
        image_size = 256
    else:
        image_size = 300

    await message.answer(text='Style transfering starts. '
                              'Wait a little bit \U0001F558',
                         reply_markup=types.ReplyKeyboardRemove())
    transform('content' + user_id + '.jpg', 'style' + user_id + '.jpg', image_size)
    with open('result' + user_id + '.jpg', 'rb') as file:
        await message.answer_photo(file, caption='Work is done!', reply_markup=buttons_for_start)
    content_flag = False
    style_flag = False
    os.remove('content' + user_id + '.jpg')
    os.remove('style' + user_id + '.jpg')
    os.remove('result' + user_id + '.jpg')
    await state.finish()


@dp.message_handler(content_types=types.ContentTypes.PHOTO, state='*')
async def catch_bad_photos(message):
    await message.answer(text='Sorry, before you send me a photo, you need to initialize me\U0001F974\n' 
                              'Press */transfer* or *button below*',
                         reply_markup=buttons_for_start, parse_mode='Markdown')


@dp.message_handler(state='*')
async def catch_bad_commands(message: types.Message):
    await message.answer(text="Sorry, I don't know this command \U0001F62C\n"
                              "Write *'/'* to see list of commands or press */help*",
                         reply_markup=buttons_for_start, parse_mode='Markdown')


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    # insert code here to run it after start


async def on_shutdown(dp):
    logging.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')


if __name__ == '__main__':
   # executor.start_polling(dp, skip_updates=True)

    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
