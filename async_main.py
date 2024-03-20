import time
from dataclasses import dataclass

import requests
import json
import pyexcel as pe
import asyncio
import aiohttp

@dataclass
class Art:
    id: int
    title: str
    url: str
    price: float

    def __post_init__(self):
        if self.price:
            self.price = self.price / 100


def get_request(page: int):
    headers = {
        'authority': 'bluethumb.com.au',
        'accept': 'application/json',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,fi;q=0.6,nb;q=0.5,is;q=0.4,pt;q=0.3,ro;q=0.2,it;q=0.1,de;q=0.1',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://bluethumb.com.au/artworks',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }

    params = {
        'per': '100',
        'page': page,
        'category': 'All Art',
        'term': '',
        'sort': 'relevant',
        'ready_to_hang': 'all',
        'from_followeds': 'all',
        'availability': 'for_sale_web',
        'featured': 'false',
        'basePath': '/artworks',
    }

    response = requests.get('https://bluethumb.com.au/api/listings',
                            params=params,
                            headers=headers)
    return response.json()


def validate_json(res_json: json) -> list[Art]:
    all_art_in_page = []
    for art in res_json["listings"]:
        all_art_in_page.append(
            Art(
                id=art["id"],
                title=art["title"],
                url=art["url"],
                price=art["price"]["cents"]
            )
        )
    return all_art_in_page


def save(list_art: list[Art]):
    data = [
        ["id", "Название", "Ссылка", "Цена"],
    ]
    for art in list_art:
        data.append([
            art.id,
            art.title,
            art.url,
            art.price
        ])
    new_book = pe.Book({"Sheet_1": data})
    new_book.save_as("art.xlsx")


def parse():
    all_art = []
    for page in range(1, 101, 1):
        res = get_request(page=page)
        all_art += validate_json(res)
    save(all_art)
async def aget_request(session, page):
    headers = {
        'authority': 'bluethumb.com.au',
        'accept': 'application/json',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,fi;q=0.6,nb;q=0.5,is;q=0.4,pt;q=0.3,ro;q=0.2,it;q=0.1,de;q=0.1',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://bluethumb.com.au/artworks',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }

    params = {
        'per': '100',
        'page': page,
        'category': 'All Art',
        'term': '',
        'sort': 'relevant',
        'ready_to_hang': 'all',
        'from_followeds': 'all',
        'availability': 'for_sale_web',
        'featured': 'false',
        'basePath': '/artworks',
    }
    async with session.get(
            url='https://bluethumb.com.au/api/listings',
            params=params,
            headers=headers
    ) as response:
        return await response.json()

async def aparse():
    async with aiohttp.ClientSession() as session:
        tasks = []
        tasks2 = []
        for i in range(1, 101, 1):
            if i % 2:
                tasks.append(aget_request(session=session, page=i))
                continue
            tasks2.append(aget_request(session=session, page=i))
        results = await asyncio.gather(*tasks)
        results2 = await asyncio.gather(*tasks2)
        all_art = []
        for result in results + results2:
            all_art += validate_json(result)
        save(all_art)

if __name__ == '__main__':
    start = time.time()
    asyncio.run(aparse())
    print(f"Успешно выполнено за {int(time.time() - start)} сек. ")
