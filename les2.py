from bs4 import BeautifulSoup as bs
import requests
from typing import List, Dict
import  re
from pymongo import MongoClient
#response = requests.get('https://geekbrains.ru/posts').text
#soup = bs(response,'lxml')

class GeekBrParse:
    doman = 'https://geekbrains.ru'
    GB_url = 'https://geekbrains.ru/posts'

    def __init__(self):
        self.client = MongoClient ('mongodb://localhost:27017')
        self.db = self.client['parse_gb_blog']
        self.collection = self.db['posts']
        self.visited_url = set () #посещенная ссылка, уникальная
        self.post_links = set ()
        self.post_data = []

    def parse_rows (self, url=GB_url):
        while url:
            if url in self.visited_url:
                break
            response = requests.get(url)
            self.visited_url.add(url)
            soup = bs(response.text, 'lxml')
            url = self.get_next_page (soup)
            self.get_post_links(soup)
            print(1)


    def get_next_page (self, soup: bs):
        ul = soup.find ('ul', attrs={'class':'gb__pagination'})
        a = ul.find('a', text=re.compile('›'))
        return f'{self.doman}{a.get("href")}' if a and a.get("href") else None

    def get_post_links (self, soup: bs):
        wrapper = soup.find('div', attrs={'class':'post-items-wrapper'})
        posts = wrapper.find_all ('div', attrs={'class': 'post-item'})
        links ={f'{self.doman}{itm.find("a").get("href")}' for itm in posts}
        self.post_links.update(links)

    def post_page(self):
        for url in self.post_links:
            if url in self.visited_url:
                continue
            response = requests.get(url)
            self.visited_url.add(url)
            soup = bs(response.text, 'lxml')
            self.post_data.append(self.get_post_data(soup))

    def get_post_data(self, soup: bs):
        result = {}
        result['title'] = soup.find('h1', attrs={'class':'blogpost-title'}).text
        content = soup.find('div', attrs={'class': 'blogpost-content', 'itemprop':'articleBody'})
        img = content.find ('img')
        result['image'] = img.get('src') if img else None
        result['writer_name'] = soup.find('time', attrs={'class':'text-lg text-dark'}).text
        content_writer_url = soup.find('div', attrs={'class': 'col-md-5 col-sm-12 col-lg-8 col-xs-12 padder-v'})
        url_wr = content_writer_url.find('a', attrs={'style':'text-decoration:none;'})
        result['writer_url'] = url_wr.get('href') if url_wr else None
        result['pub_date'] = soup.find('time', attrs={'class':'text-md text-muted m-r-md'}).datetime object
        return result

    def save_to_mongo(self):
        self.collection.insert_many(self.posts_data)







if __name__ == '__main__':
    parser = GeekBrParse ()
    parser.parse_rows()
    parser.post_page()
    parser.save_to_mongo()

    print(1)