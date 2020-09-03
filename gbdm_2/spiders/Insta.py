import json
import scrapy
from scrapy.http.response import Response
from pymongo import MongoClient


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']

    __login_url = 'https://www.instagram.com/accounts/login/ajax/'
    __tag_url = '/explore/tags/Беларусь>/'

    __api_tag_url = '/graphql/query/'
    __query_hash = 'c769cb6c71b24c8a86590b22402fda50'

    def __init__(self, *args, **kwargs):
        self.__login = kwargs['login']
        self.__password = kwargs['password']
        super().__init__(*args, **kwargs)
        self.client = MongoClient('mongodb://localhost:27017')
        self.db = self.client['parse_gb_blog']

    def parse(self, response: Response, **kwargs):
        try:
            js_data = self.get_js_shared_data(response)

            yield scrapy.FormRequest(self.__login_url,
                                     method='POST',
                                     callback=self.parse,
                                     formdata={
                                         'username': self.__login,
                                         'enc_password': self.__password
                                     },
                                     headers={'X-CSRFToken': js_data['config']['csrf_token']}
                                     )
        except AttributeError as e:
            if response.json().get('authenticated'):
                yield response.follow(self.__tag_url, callback=self.tag_page_parse)

    def tag_page_parse(self, response: Response):
        js_data = self.get_js_shared_data(response)
        hashtag: dict = js_data['entry_data']['TagPage'][0]['graphql']['hashtag']


        if hashtag ['edge_hashtag_to_media']['page_info']['has_next_page']:
            variables = {"tag_name": hashtag['name'],
                         "first": 60,
                        "after": hashtag['edge_hashtag_to_media']['page_info']['end_cursor']}

            url = f'{self.__api_tag_url}?query_hash={self.__query_hash}&variables={json.dumps(variables, ensure_ascii=False)}'
            yield response.follow(url, callback=self.get_api_hastag_posts)

        hashtag['posts_count'] = hashtag['edge_hashtag_to_media']['count']
        posts: list = hashtag.pop('edge_hashtag_to_media')['edges']

        yield InstaHashTagItem(data=hashtag)

        for post in posts:
            yield InstaPostItem(data=post['node'])
            print(1)
            if post['node']['edge_media_to_comment']['count'] > 40 or post['node']['edge_liked_by']['count'] > 100:
                yield response.follow(f'/p/{post["node"]["shortcode"]}/',
                                      callback=self.post_page_parse)

    def post_page_parse(self, response):
        data = self.get_js_shared_data(response)
        yield InstaUserItem(data=data['entry_data']['PostPage'][0]['graphq1']['shortcode_media']['owner'])


    def get_api_hastag_posts(self, response: Response):
        hashtag = response.json()['data']['hashtag']
        if hashtag ['edge_hasgtag_to_media']['page_info']['has_next_page']:
            variables = {"tag_name": hashtag['name'],
                         "first": 60,
                        "after": hashtag['edge_hashtag_to_media']['page_info']['end_cursor']}
            url = f'{self.__api_tag_url}?query_hash={self.__query_hash}&variables={json.dumps(variables, ensure_ascii=False)}'
            yield response.follow(url, callback=self.get_api_hastag_posts)
        posts: list = hashtag.pop('edge_hashtag_to_media')['edges']

        for post in posts:
            yield InstaPostItem(data=post['node'])
            print(1)
            if post['node']['edge_media_to_comment']['count'] > 40 or post['node']['edge_liked_by']['count'] > 100:
                yield response.follow(f'/p/{post["node"]["shortcode"]}/',
                                      callback=self.post_page_parse)

    @staticmethod
    def get_js_shared_data(response):
        marker = "window._sharedData = "
        data = response.xpath(
            f'/html/body/script[@type="text/javascript" and contains(text(), "{marker}")]/text()'
        ).extract_first()
        data = data.replace(marker, '')[:-1]
        return json.loads(data)

    def save_to_mongo(self):
        self.collection.insert_many(self.parse_1)