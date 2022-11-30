import os
from asyncio import sleep

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hbold, hcode, hlink
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from settings import TM_TOKEN, PROXY_URL, URL, TIMER
from main import get_data, check_cars_update

bot = Bot(token=TM_TOKEN, parse_mode=types.ParseMode.HTML, proxy=PROXY_URL)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Allowed users
user_id_required = [
    364022,  # Gridnev
    444851768,  # Fedorov
]

# Change for use in groups (user_id == chat_id in pm)
chat_id_required = user_id_required


class Parm(StatesGroup):
    status = State()


# Starts process and went to general menu
@dp.message_handler(user_id=user_id_required, commands="start")
async def start_handler(message: types.Message):
    """
    Create Buttons menu
    :param message:
    :return:
    """
    start_buttons = ["Начать процесс"]
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True, row_width=3, selective=True
    )
    keyboard.add(*start_buttons)
    await message.answer("Выберете метод", reply_markup=keyboard)


# Went to general menu
@dp.message_handler(Text(equals="Начать процесс"), user_id=user_id_required)
async def start(message: types.Message, state: FSMContext):
    """
    Move to the menu above
    :param state:
    :param message:
    :return:
    """

    start_buttons = ["Остановить"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer("Процесс начат", reply_markup=keyboard)
    async with state.proxy() as data:
        data["status"] = True
    while True:
        await sleep(TIMER)
        async with state.proxy() as data:
            if data["status"] is False:
                break
        if not os.path.exists("cars.json") or os.stat("cars.json").st_size == 0:
            cars_data = get_data(site_url=URL)
            if cars_data is not {}:
                for car_id in cars_data:
                    car_name = cars_data[car_id]["car_name"]
                    car_engine = cars_data[car_id]["car_engine"]
                    car_chassis = cars_data[car_id]["car_chassis"]
                    car_price = cars_data[car_id]["car_price"]
                    date = cars_data[car_id]["date"]
                    car_link = cars_data[car_id]["car_link"]
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
            cars_data = check_cars_update(site_url=URL)
            if cars_data is not {}:
                for car_id in cars_data:
                    car_name = cars_data[car_id]["car_name"]
                    car_engine = cars_data[car_id]["car_engine"]
                    car_chassis = cars_data[car_id]["car_chassis"]
                    car_price = cars_data[car_id]["car_price"]
                    date = cars_data[car_id]["date"]
                    car_link = cars_data[car_id]["car_link"]
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


# Went to general menu
@dp.message_handler(state=Parm.status)
@dp.message_handler(Text(equals="Остановить"), user_id=user_id_required)
async def stop(message: types.Message, state: FSMContext):
    """
    Move to the menu above
    :param state:
    :param message:
    :return:
    """
    start_buttons = ["Начать процесс"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    async with state.proxy() as data:
        data["status"] = False
    await sleep(3)
    await state.finish()
    await message.answer("Процесс остановлен", reply_markup=keyboard)


# Init bot
def main():
    executor.start_polling(dp)
    # executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
