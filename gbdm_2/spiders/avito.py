import scrapy
from typing import List, Dict
from scrapy.loader import ItemLoader #принимать запросы и выполнять их под капотом
#from pymongo import MongoClient

from gbdm.items import AvitoItem

class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['www.avito.ru']
    start_urls = ['https://www.avito.ru/novosibirsk/kvartiry/prodam']

    __xpath_query = {
        'pagination': '//div[@class="index-content-2lnSO"]//'
                      'div[contains(@data-marker, "pagination-button")]/'
                      'span[@class="pagination-item-1WyVp"]/@data-marker',

        'ads': '//h3[@class="snippet-title"]/a[@class="snippet-link"][@itemprop="url"]/@href',

        'title': '//h1[@class="title-info-title"]/span[@itemprop="name"]/text()',

        'images': '//div[contains(@class, "gallery-imgs-container")]'
                  '/div[contains(@class, "gallery-img-wrapper")]'
                  '/div[contains(@class, "gallery-img-frame")]/@data-url',

        'address': '//div[@itemprop="address"]/span/text()',
      }

    def __init__(self):
        self.client = MongoClient ('mongodb://localhost:27017')
        self.db = self.client['parse_gb_blog']

    def parse(self, response, start=True):
        if start:
            pages_count = int(
                response.xpath(self.__xpath_query['pagination']).extract()[-1].split('(')[-1].replace(')', ''))

            for num in range(2, pages_count + 1):
                yield response.follow(
                    f'?p={num}',
                    callback=self.parse,
                    cb_kwargs={'start': False}
                )

        for link in response.xpath(self.__xpath_query['ads']):
            yield response.follow(
                link,
                callback=self.ads_parse

            )

    def ads_parse(self, response):

        item_loader = ItemLoader(AvitoItem(), response)
        for key, value in self.__xpath_query.items():
            if key in ('pagination', 'ads'):
                continue
            item_loader.add_xpath(key, value)
        item_loader.add_value('url', response.url)

        yield item_loader.load_item()



    def parse_1(self, response):

        item_loader = ItemLoader(AvitoItem(), response)
        for key, value in self.__xpath_query.items():
            if key in ('pagination', 'ads'):
                continue
            item_loader.add_xpath(key, value)
        item_loader.add_value('url', response.url)

        yield item_loader.load_item()



    #def save_to_mongo(self):
        #self.collection.insert_many(self.parse_1)