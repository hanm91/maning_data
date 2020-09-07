import requests

USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Mobile Safari/537.36'

api_url_5ka = 'https://5ka.ru/api/v2/special_offers/'


class Parser5ka:
    USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Mobile Safari/537.36'

    def __init__(self, api_url):
        self.api_url = api_url
        self.next = api_url
        self.prev = None
        self.result = []

    def parse(self):
        while True:
            if self.next == self.api_url:
                response = requests.get(self.next, params={'records_per_page': 100},
                                        headers={'User-Agent': self.USER_AGENT})
            elif self.next:
                response = requests.get(self.next, headers={'User-Agent': self.USER_AGENT})

            else:
                break

            data = response.json()
            self.result.extend(data.get('results'))
            self.next = data.get('next')
            self.prev = data.get('previous')
            print(len(self.result))


if __name__ == '__main__':
    testing = Parser5ka(api_url_5ka)
    testing.parse()
    print(1)

