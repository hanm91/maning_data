import random
import asyncio

import re
import requests
import aiohttp
from bs4 import BeautifulSoup
from pymongo import MongoClient

from les3_1_DB import HabroDB
from les3_1_models import Writer, Tag, Post


class HabrParser:
    domain = 'https://habr.com'
    start_url = 'https://habr.com/ru/top/'
    headers = {
        "User-Agent": "Mozilla / 5.0(Linux; Android 6.0; Nexus  5  Build / MRA58N) "
                      "AppleWebKit / 537.36 "
                      "(KHTML, like  Gecko) Chrome / 84.0.4147.135 Mobile Safari / 537.36"
    }

    def __init__(self, db):
        self.db: HabroDB = db
        self.timeout = aiohttp.ClientTimeout(total=100.0)

    async def request(self, url) -> BeautifulSoup:
        while True:
            await asyncio.sleep(random.randint(1, 4) / random.randint(2, 6))
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.get(url, headers=self.headers) as response:
                        if response.status == 200:
                            soap = BeautifulSoup(await response.text(), 'lxml')
                            break
                        elif response.status >= 500:
                            await asyncio.sleep(1.3)
                            continue
            except aiohttp.ServerDisconnectedError:
                await asyncio.sleep(0.3)
                continue
            except aiohttp.ClientPayloadError:
                await asyncio.sleep(0.3)
                continue
        return soap

    async def parse(self, url=start_url):
        while url:
            soap = await self.request(url)
            url = self.get_next_page(soap)
            await asyncio.wait([self.posts_parse(url) for url in self.search_post_links(soap)])

    async def posts_parse(self, url):
        soap = await self.request(url)
        await self.get_post_data(soap, url)

    def get_next_page(self, soap: BeautifulSoup) -> str:
        a = soap.find('a', attrs={'id': 'next_page'})
        return f'{self.domain}{a.get("href")}' if a and a.get("href") else None

    def search_post_links(self, soap: BeautifulSoup):
        posts_list = soap.find('div', attrs={'class': 'posts_list'})
        posts_a = posts_list.find_all('a', attrs={'class': 'post__title_link'})
        return {f'{itm.get("href")}' for itm in posts_a}


    async def get_post_data(self, soap: BeautifulSoup, url: str):
        result = {'url': url,
                  'title': soap.find('span', attrs={'class': 'post__title-text'}).text,
                  'writer': await self.get_writer(soap),
                  'tags': self.get_tags(soap)
                  }
        print(1)
        self.db.add_post(Post(**result))


    async def get_writer(self, soap: BeautifulSoup):
        author_block = soap.find('div', attrs={'class': 'author-panel'})
        user_info = author_block.find('div', attrs={'class': 'user-info'})
        writer_soap = await self.request(user_info.find('a').get('href'))
        writer = {
            'name': writer_soap.find('h1').find('a').text,
            'url': user_info.find('a').get('href'),
            'username': user_info.get('data-user-login')
        }
        result = Writer(**writer)

        return result

    def get_tags(self, soap: BeautifulSoup):
        tag_list = soap.find('dl', attrs={'class': 'post__tags'}).find('ul').find_all('a', attrs={'class': 'post__tag'})
        return [Tag(name=itm.text, url=itm.get('href')) for itm in tag_list]

    def get_habs(self, soap: BeautifulSoup):
        pass


if __name__ == '__main__':
    db = HabroDB('sqlite:///habr_blog1.db')
    parser = HabrParser(db)
    asyncio.run(parser.parse())