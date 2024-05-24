import json

import requests

from bs4 import BeautifulSoup as Bs

from settings import PROXY_URL


def get_image_url(domain, car_id):
    proxies = {}
    if PROXY_URL != "":
        proxies = {
            "http": PROXY_URL,
            "https": PROXY_URL,
        }
    url = f"{domain}/sale/{car_id}/?f[category_id]=1&f[brand_id]=42&f[to_order]=0&sort=newest&index=0"
    response = requests.get(url, proxies=proxies)
    soup = Bs(response.text, "lxml")
    car_images = soup.find(
        "img", class_="photo-gallery__item photo-gallery__item-main js-photo-main"
    )
    car_images = car_images.get("src") if car_images else None
    # print(soup)
    # print(car_images)
    return car_images


def get_data(site_url: str, user_id: str, domain: str):
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
        # car_image = f'{car.find("img", class_="js-sale-image").get("src")}'
        # print(f'{car.find("img", class_="js-sale-image").get("src")}')
        car_image = get_image_url(domain=domain, car_id=car_id)

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


def check_cars_update(site_url: str, user_id: str, domain: str):
    with open(f"cache/cars_{user_id}.json") as file:
        cars_list = json.load(file)

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
        car_price = car.find("div", class_="sale-price").text.strip()
        # print(cars_list[car_id]["car_price"])
        # print(car_price)
        if car_id in cars_list and cars_list[car_id]["car_price"] == car_price:
            continue
        else:
            link = f'{domain}{car.find("a", class_="sale-link").get("href")}'
            name = car.find("a", class_="sale-link").text.strip()
            car_engine = car.find("div", class_="sale-engine").text.strip()
            car_chassis = car.find("div", class_="sale-chassis").text.strip()
            # additional = car.find("div", class_="sale-additional").text.strip()
            car_price = car.find("div", class_="sale-price").text.strip()
            date = car.find("div", class_="sale-published-date").text.strip()

            # car_image = f'{car.find("img", class_="js-sale-image").get("src")}'
            car_image = get_image_url(domain=domain, car_id=car_id)

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


# check_cars_update(
#     site_url="https://autokochka.ru/sales/auto?f%5Bcategory_id%5D=1&sort=newest&f%5Bbrand_id%5D=42&f%5Bto_order%5D=0",
#     user_id="364022", domain="https://autokochka.ru")

# get_image_url(domain="https://autokochka.ru", car_id=1639327)
