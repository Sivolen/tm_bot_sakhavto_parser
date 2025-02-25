import asyncio
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    # ReplyKeyboardRemove,
)
from aiogram.utils.markdown import hbold, hcode, hlink
from aiogram.methods import DeleteWebhook

from main import get_data, check_cars_update
from settings import TM_TOKEN, PROXY_URL, TIMER, DOMAIN, USER_ID_REQUIRED, URLS

# Init states machine
storage = MemoryStorage()

session = AiohttpSession(
    proxy={
        PROXY_URL,
        # "protocol1://user:password@host1:port1",
        # ("protocol2://host2:port2", auth),
    }  # can be any iterable if not set
)

# Init Bot
form_router = Router()
dp = Dispatcher()
dp.include_router(form_router)

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


file_header = RotatingFileHandler("logs/bot.log", maxBytes=100000, backupCount=100)
file_header.setLevel(logging.DEBUG)
log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_header.setFormatter(log_format)
logger.addHandler(file_header)


# Allowed users
user_id_required = USER_ID_REQUIRED
# Change for use in groups (user_id == chat_id in pm)
chat_id_required = USER_ID_REQUIRED


class Parm(StatesGroup):
    """
    Class for states machine
    """

    # on, off switcher
    status = State()


# Starts process and went to general menu


async def start_process(message: types.Message) -> None:
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=3,
        selective=True,
        keyboard=[
            [
                KeyboardButton(text="Начать процесс"),
                KeyboardButton(text="Add Url"),
            ]
        ],
    )
    await message.answer("Выберете метод", reply_markup=keyboard)


async def start_parce(message: types.Message) -> None:
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(text="Остановить"),
            ]
        ],
    )
    await message.answer("Процесс начат", reply_markup=keyboard)


async def stop_process(message: types.Message) -> None:
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=3,
        selective=True,
        keyboard=[
            [
                KeyboardButton(text="Начать процесс"),
            ]
        ],
    )
    await message.answer("Процесс остановлен", reply_markup=keyboard)


async def send_car_data(message: types.Message, car_id: dict) -> None:
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


# @dp.message(F.from_user.id.in_(user_id_required1), Command(commands=["start"]))
@form_router.message(F.from_user.id.in_(user_id_required), Command(commands=["start"]))
async def start_handler(message: Message) -> None:
    """
    Create Buttons menu
    :param message:
    :return:
    """
    logger.info(
        f"User {message.from_user.full_name}, id: {message.from_user.id} init process"
    )

    await start_process(message)


# @dp.message(~F.from_user.id.in_(user_id_required1), Command(commands=["start"]))
@form_router.message(~F.from_user.id.in_(user_id_required), Command(commands=["start"]))
async def start_handler(message: Message) -> None:
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
@form_router.message(F.from_user.id.in_(user_id_required), F.text == "Начать процесс")
async def start(message: types.Message, state: FSMContext) -> None:
    """
    Move to the menu above
    :param state:
    :param message:
    :return:
    """
    logger.info(
        f"User {message.from_user.full_name}, id: {message.from_user.id} starting process"
    )
    await state.set_state(Parm.status)

    # init keyboad
    await start_parce(message)

    user_id: int = message.from_user.id
    await state.update_data(status={user_id: {"status": True}})
    while True:
        # Checking the process, if true then it works, if false then interrupt the loop
        state_data: dict = await state.get_data()
        if state_data["status"][user_id]["status"] is False:
            logger.info(
                f"User {message.from_user.full_name}, id: {message.from_user.id} process status: {message.from_user.id}"
            )
            # await state.clear()
            break
        URL: str = URLS.get(str(message.from_user.id))
        if not URL:
            await message.answer("URL not found")
            await stop_process(message)
            break
        cache_file: str = f"cache/cars_{message.from_user.id}.json"
        if not os.path.exists(cache_file) or os.path.getsize(cache_file) == 0:
            cars_data: dict = get_data(
                site_url=URL, user_id=str(user_id), domain=DOMAIN
            )
        else:
            cars_data: dict = check_cars_update(
                site_url=URL, user_id=str(user_id), domain=DOMAIN
            )

        if cars_data is not {}:
            logger.info(
                f"User {message.from_user.full_name}, id: {message.from_user.id} process status: send {cars_data}"
            )
            for k, car_id in sorted(cars_data.items()):
                await send_car_data(message, car_id)

        # Timeout before next request
        await asyncio.sleep(TIMER)


# Stop parsing
@form_router.message(
    Parm.status, F.from_user.id.in_(user_id_required), F.text == "Остановить"
)
# @dp.message(Text(contains="Остановить"))
async def stop(message: types.Message, state: FSMContext) -> None:
    """
    Move to the menu above
    :param state:
    :param message:
    :return:
    """
    logger.info(
        f"User {message.from_user.full_name}, id: {message.from_user.id} stopping process"
    )
    user_id = message.from_user.id
    await state.update_data(status={user_id: {"status": False}})

    await stop_process(message)


# Init bot
async def main() -> None:
    # bot = Bot(token=TM_TOKEN, parse_mode="HTML", session=session)
    bot = Bot(
        token=TM_TOKEN, default=DefaultBotProperties(parse_mode="HTML"), session=session
    )
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


# Point
if __name__ == "__main__":
    # main()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
