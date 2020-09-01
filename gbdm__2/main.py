from scrapy.crawler import CrawlerProcess # основной клвсс в экзепляре которого будут раб поуки
from scrapy.settings import Settings

from gbdm import settings
from gbdm.spiders.yula import YoulaAutoSpider

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule(settings) # втсаляем клсс сетингс

    craw_proc = CrawlerProcess(settings=crawl_settings)

    craw_proc.crawl(YoulaAutoSpider)

    craw_proc.start() # паук будет запщун