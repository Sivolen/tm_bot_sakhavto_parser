import os

import logging
from logging.handlers import RotatingFileHandler
import sys
import asyncio
from asyncio import sleep

from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.utils.markdown import hbold, hcode, hlink
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, Text
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    # ReplyKeyboardRemove,
)

from settings import TM_TOKEN, PROXY_URL, URL, TIMER, DOMAIN

from main import get_data, check_cars_update

# bot = Bot(token=TM_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
# dp = Dispatcher(bot, storage=storage)

session = AiohttpSession(
    proxy={
        PROXY_URL,
        # "protocol1://user:password@host1:port1",
        # ("protocol2://host2:port2", auth),
    }  # can be any iterable if not set
)

form_router = Router()


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


# user_id_required = [
#     364022,  # Gridnev
#     444851768,  # Fedorov
#     299491767,  # Kim A.E.
# ]
# Allowed users

user_id_required = {
    364022,  # Gridnev
    444851768,  # Fedorov
    299491767,  # Kim A.E.
}
# Change for use in groups (user_id == chat_id in pm)
chat_id_required = user_id_required


class Parm(StatesGroup):
    """
    Class for states machine
    """

    # on, off switcher
    status = State()


# Starts process and went to general menu

# @dp.message(F.from_user.id.in_(user_id_required1), Command(commands=["start"]))
@form_router.message(F.from_user.id.in_(user_id_required), Command(commands=["start"]))
async def start_handler(message: Message, state: FSMContext):
    """
    Create Buttons menu
    :param message:
    :return:
    """
    logger.info(
        f"User {message.from_user.full_name}, id: {message.from_user.id} init process"
    )
    await state.set_state(Parm.status)
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True, row_width=3, selective=True,
        keyboard=[
            [
                KeyboardButton(text="Начать процесс"),
            ]

        ]
    )

    await message.answer("Выберете метод", reply_markup=keyboard)


# @dp.message(~F.from_user.id.in_(user_id_required1), Command(commands=["start"]))
@form_router.message(~F.from_user.id.in_(user_id_required), Command(commands=["start"]))
async def start_handler(message: Message):
    """
    Create Buttons menu
    :param message:
    :return:
    """
    logger.info(
        f"User {message.from_user.full_name}, id: {message.from_user.id} init process"
    )

    await message.answer("Операция не позволена")


# Start parsing
# @dp.message(Text(contains="Начать процесс"))
@form_router.message(F.from_user.id.in_(user_id_required), Text(contains="Начать процесс"))
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
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(text="Остановить"),
            ]
        ]
    )
    await message.answer("Процесс начат", reply_markup=keyboard)
    user_id = message.from_user.id
    await state.update_data(status={
        user_id: {"status": True}
    })

    # current_state = await state.get_state()
    # state_data = await state.get_data()

    # print(current_state)
    # print(state_data)
    while True:
        # Checking the process, if true then it works, if false then interrupt the loop
        state_data = await state.get_data()
        if state_data["status"][user_id]["status"] is False:
            print("test")
            logger.info(
                f'User {message.from_user.full_name}, id: {message.from_user.id} process status: {message.from_user.id}'
            )
            await state.clear()
            break
        if (
            not os.path.exists(f"cache/cars_{message.from_user.id}.json")
            or os.stat(f"cache/cars_{message.from_user.id}.json").st_size == 0
        ):
            cars_data = get_data(site_url=URL, user_id=str(user_id), domain=DOMAIN)
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
            cars_data = check_cars_update(site_url=URL, user_id=str(user_id), domain=DOMAIN)
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

        # Timeout before next request
        await sleep(TIMER)


# Stop parsing
@form_router.message(Parm.status, F.from_user.id.in_(user_id_required), F.text.casefold() == "остановить")
# @dp.message(Text(contains="Остановить"))
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
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True, row_width=3, selective=True,
        keyboard=[
            [
                KeyboardButton(text="Начать процесс"),
            ]

        ]
    )
    user_id = message.from_user.id
    await state.update_data(status={
        user_id: {"status": False}
    })

    await message.answer("Процесс остановлен", reply_markup=keyboard)


# Init bot
# def main():
#     # executor.start_polling(dp)
#     # executor.start_polling(dp, skip_updates=True)
#     dp.start_polling()

async def main():
    bot = Bot(token=TM_TOKEN, parse_mode="HTML", session=session)

    dp = Dispatcher()

    dp.include_router(form_router)

    await dp.start_polling(bot)


# Point
if __name__ == "__main__":
    # main()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
