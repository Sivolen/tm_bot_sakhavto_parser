import os

import logging
from logging.handlers import RotatingFileHandler

from asyncio import sleep

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hbold, hcode, hlink
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from settings import TM_TOKEN, PROXY_URL, URL, TIMER, DOMAIN
from main import get_data, check_cars_update

bot = Bot(token=TM_TOKEN, parse_mode=types.ParseMode.HTML, proxy=PROXY_URL)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Configure logging default
logging.basicConfig(
    level=logging.DEBUG,
    filename="logs/debug.log",
    filemode="w",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    encoding="utf-8",
)

# Init logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Configure log dimp to the file
# Set logger format
file_header = RotatingFileHandler("logs/bot.log", maxBytes=100000, backupCount=100)
file_header.setLevel(logging.DEBUG)
log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_header.setFormatter(log_format)
logger.addHandler(file_header)


# Allowed users
user_id_required = [
    364022,  # Gridnev
    444851768,  # Fedorov
    299491767,  # Kim A.E.
]

# Change for use in groups (user_id == chat_id in pm)
chat_id_required = user_id_required


class Parm(StatesGroup):
    """
    Class for states machine
    """

    # on, off switcher
    status = State()


# Starts process and went to general menu
@dp.message_handler(user_id=user_id_required, commands="start")
async def start_handler(message: types.Message):
    """
    Create Buttons menu
    :param message:
    :return:
    """
    logger.info(
        f"User {message.from_user.full_name}, id: {message.from_user.id} init process"
    )
    start_buttons = ["Начать процесс"]
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True, row_width=3, selective=True
    )
    keyboard.add(*start_buttons)
    await message.answer("Выберете метод", reply_markup=keyboard)


# Start parsing
@dp.message_handler(Text(equals="Начать процесс"), user_id=user_id_required)
async def start(message: types.Message, state: FSMContext):
    """
    Move to the menu above
    :param state:
    :param message:
    :return:
    """
    logger.info(
        f"User {message.from_user.full_name}, id: {message.from_user.id} starting process"
    )
    start_buttons = ["Остановить"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer("Процесс начат", reply_markup=keyboard)
    async with state.proxy() as data:
        data[message.from_user.id] = True
    while True:
        # Timeout before next request
        await sleep(TIMER)
        # Checking the process, if true then it works, if false then interrupt the loop
        async with state.proxy() as data:
            logger.info(
                f'User {message.from_user.full_name}, id: {message.from_user.id} process status: {message.from_user.id}'
            )
            if data[message.from_user.id] is False:
                await state.finish()
                break
        if (
            not os.path.exists(f"cache/cars_{message.from_user.id}.json")
            or os.stat(f"cache/cars_{message.from_user.id}.json").st_size == 0
        ):
            cars_data = get_data(site_url=URL, user_id=message.from_user.id, domain=DOMAIN)
            if cars_data is not {}:
                for k, car_id in sorted(cars_data.items()):
                    car_name = car_id["car_name"]
                    car_engine = car_id["car_engine"]
                    car_chassis = car_id["car_chassis"]
                    car_price = car_id["car_price"]
                    date = car_id["date"]
                    car_link = car_id["car_link"]
                    massage_ = (
                        f"{hbold('Модель: ')}{car_name}\n"
                        f"{hcode('Вид двигателя: ')}{car_engine}\n"
                        f"{hcode('Привод: ')}{car_chassis}\n"
                        f"{hcode('Цена: ')}{car_price}\n"
                        f"{hcode('Дата: ')}{date}\n"
                        f"{hlink('Просмотреть', car_link)}"
                    )
                    await message.answer(massage_)
        else:
            cars_data = check_cars_update(site_url=URL, user_id=message.from_user.id, domain=DOMAIN)
            if cars_data is not {}:
                logger.info(
                    f"User {message.from_user.full_name}, id: {message.from_user.id} process status: {cars_data}"
                )
                for k, car_id in sorted(cars_data.items()):
                    car_name = car_id["car_name"]
                    car_engine = car_id["car_engine"]
                    car_chassis = car_id["car_chassis"]
                    car_price = car_id["car_price"]
                    date = car_id["date"]
                    car_link = car_id["car_link"]
                    massage_ = (
                        f"{hbold('Модель: ')}{car_name}\n"
                        f"{hcode('Вид двигателя: ')}{car_engine}\n"
                        f"{hcode('Привод: ')}{car_chassis}\n"
                        f"{hcode('Цена: ')}{car_price}\n"
                        f"{hcode('Дата: ')}{date}\n"
                        f"{hlink('Просмотреть', car_link)}"
                    )
                    await message.answer(massage_)
        await Parm.status.set()


# Stop parsing
@dp.message_handler(state=Parm.status)
@dp.message_handler(Text(equals="Остановить"), user_id=user_id_required)
async def stop(message: types.Message, state: FSMContext):
    """
    Move to the menu above
    :param state:
    :param message:
    :return:
    """
    logger.info(
        f"User {message.from_user.full_name}, id: {message.from_user.id} stopping process"
    )
    start_buttons = ["Начать процесс"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    async with state.proxy() as data:
        data[message.from_user.id] = False
    await message.answer("Процесс остановлен", reply_markup=keyboard)


# Init bot
def main():
    # executor.start_polling(dp)
    executor.start_polling(dp, skip_updates=True)


# Point
if __name__ == "__main__":
    main()
