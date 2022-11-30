import json

# import os

import requests

from bs4 import BeautifulSoup as Bs

from settings import PROXY_URL


def get_data(site_url: str, user_id: str):

    domain = "https://autosakhcom.ru"
    proxies = {}
    if PROXY_URL != "":
        proxies = {
            "http": PROXY_URL,
            "https": PROXY_URL,
        }

    response = requests.get(site_url, proxies=proxies)

    soup = Bs(response.text, "lxml")

    cars = soup.findAll("div", class_="sale-item")
    cars_dict = {}
    for car in cars:
        car_id = car.find("a", class_="sale-link").get("href").split("/")[2]
        link = f'{domain}{car.find("a", class_="sale-link").get("href")}'
        name = car.find("a", class_="sale-link").text.strip()
        car_engine = car.find("div", class_="sale-engine").text.strip()
        car_chassis = car.find("div", class_="sale-chassis").text.strip()
        # additional = car.find("div", class_="sale-additional").text.strip()
        car_price = car.find("div", class_="sale-price").text.strip()
        date = car.find("div", class_="sale-published-date").text.strip()
        car_image = f'{domain}{car.find("img", class_="js-sale-image").get("src")}'

        cars_dict[car_id] = {
            "car_id": car_id,
            "car_link": link,
            "car_name": name,
            "car_engine": car_engine,
            "car_chassis": car_chassis,
            "car_price": car_price,
            "car_image": car_image,
            "date": date,
        }

    with open(f"cache/cars_{user_id}.json", "w") as file:
        json.dump(cars_dict, file, indent=4, ensure_ascii=False)
    return cars_dict


def check_cars_update(site_url: str, user_id: str):
    with open(f"cache/cars_{user_id}.json") as file:
        cars_list = json.load(file)

    domain = "https://autosakhcom.ru"

    proxies = {}
    if PROXY_URL != "":
        proxies = {
            "http": PROXY_URL,
            "https": PROXY_URL,
        }

    response = requests.get(site_url, proxies=proxies)
    soup = Bs(response.text, "lxml")

    cars = soup.findAll("div", class_="sale-item")
    new_cars_dict = {}
    for car in cars:
        car_id = car.find("a", class_="sale-link").get("href").split("/")[2]
        if car_id in cars_list:
            continue
        else:
            link = f'{domain}{car.find("a", class_="sale-link").get("href")}'
            name = car.find("a", class_="sale-link").text.strip()
            car_engine = car.find("div", class_="sale-engine").text.strip()
            car_chassis = car.find("div", class_="sale-chassis").text.strip()
            # additional = car.find("div", class_="sale-additional").text.strip()
            car_price = car.find("div", class_="sale-price").text.strip()
            date = car.find("div", class_="sale-published-date").text.strip()
            car_image = f'{domain}{car.find("img", class_="js-sale-image").get("src")}'

            cars_list[car_id] = {
                "car_id": car_id,
                "car_link": link,
                "car_name": name,
                "car_engine": car_engine,
                "car_chassis": car_chassis,
                "car_price": car_price,
                "car_image": car_image,
                "date": date,
            }

            new_cars_dict[car_id] = {
                "car_id": car_id,
                "car_link": link,
                "car_name": name,
                "car_engine": car_engine,
                "car_chassis": car_chassis,
                "car_price": car_price,
                "car_image": car_image,
                "date": date,
            }
    with open(f"cache/cars_{user_id}.json", "w") as file:
        json.dump(cars_list, file, indent=4, ensure_ascii=False)

    return new_cars_dict


#
#
# #
# if __name__ == "__main__":
#     url = (
#         "https://autosakhcom.ru/sales/auto"
#         "?f%5Bcategory_id%5D=1&is_extended=1&f%5Bprice_e%5D=300000&f%5Bto_order%5D=0&sort=newest#search-description"
#     )
#     # get_data(site_url=url)
#     # if not os.path.exists("cars.json") or os.stat("cars.json").st_size == 0:
#     #     print(get_data(site_url=url))
#     # else:
#     #     print(check_cars_update(site_url=url))
#     # get_data(site_url=url)
#     test = check_cars_update(site_url=url)
#     print(test)
#     for k, car_id in sorted(test.items()):
#         car_name = car_id["car_name"]
#         car_engine = car_id["car_engine"]
#         car_chassis = car_id["car_chassis"]
#         car_price = car_id["car_price"]
#         date = car_id["date"]
#         car_link = car_id["car_link"]
#         massage_ = (
#             f"{('Модель: ')}{car_name}\n"
#             f"{('Вид двигателя: ')}{car_engine}\n"
#             f"{('Привод: ')}{car_chassis}\n"
#             f"{('Цена: ')}{car_price}\n"
#             f"{('Дата: ')}{date}\n"
#             f"{('Просмотреть', car_link)}"
#         )
#         print(massage_)
