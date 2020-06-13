import requests
from bs4 import BeautifulSoup

from pinterest import LoggingUtil

logging = LoggingUtil.get_logging()


pre_url = 'https://www.pinterest.com/search/pins/?q=#{keyword}'


class PinterestSearchImprovement:

    @staticmethod
    def __get_headers(request_cookie):
        headers = {'Host': 'www.pinterest.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
                   'Accept': 'application/json, text/javascript, */*, q=0.01',
                   'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                   'Accept-Encoding': 'gzip, deflate',
                   'Referer': 'https://www.pinterest.com/',
                   'X-Requested-With': 'XMLHttpRequest',
                   'X-APP-VERSION': '8e90ffe',
                   'X-Pinterest-AppState': 'active',
                   'Connection': 'close',
                   'Cookie': request_cookie
                   }
        return headers

    def __init__(self, request_cookie):
        super().__init__()
        self.headers = self.__get_headers(request_cookie)

    def get_recommend(self, keyword):
        try:
            request_url = pre_url.replace('#{keyword}', keyword)

            response = requests.get(request_url, headers=self.headers)
            logging.info("keyword=%s, status=%s", keyword, response.status_code)

            try:
                soup = BeautifulSoup(response.text, features="html.parser")
                elements = soup.select('div.SearchImprovementsBar-OuterScrollContainer a[data-test-id="search-guide"]')
                keywords = [e.get_text() for e in elements]
                return ','.join(keywords)
            except Exception as e:
                logging.exception('keyword=%s', keyword)

        except Exception as e:
            logging.exception('error: keyword=%s', keyword)


if __name__ == '__main__':
    cookie = '_auth=1;_b=AUxXd9j4kaBNg7DJdzeMVo/HN+frn25+JB12oIIhcU911x6c5K31IGSsWZcQJ4xamO0=;_pinterest_sess=TWc9PSZQdkRTQmxqSGliSTFSRTZxa1pDRU1NL1gzcVpNREp0QTRUaGdMZ29lUHBEVk1mZTUrb1dPbzJtSE5LWjAybTk0VW01WWEyaTJzMUs4dng0ZjFvOVFhMVlxZENkR1dTb2lCYmVodkNGSlB1Y2FMTHMzNXJ4Z2tLeWNPaE8zdmtLdEs5eVdrUDdyTFowZHlJK1l4dzBpWUNBNlQ4Sm0xVWgxSEFXNFViMS9sY3JtUGxUbXNwQ2ZQMG14NldodXpHSWNkS0x4b2J6eGU4NHllVTYyWXpPbHpEenNUa0M1Vy84WkppN0MrcHRlN1F0OHdMN2xPNXhqRnkxMkxtdDA3U0YxWExGdWxXMjV5cUR1ZEZlN2VTNGM0NXhHYTFDeWU2S2FWRjEwQW4xSmdiNlhobUFBQUZ0dWNiMGNGWmt5eW9BZGVHUDJWWVFzZ0xNWXROZ2JoTEUzU2FoQTV3Ym5INXVISWhaNlVwaytiNWJVbFhGcGFyMWFvSlpIR1NsNGJpSldtQ3VoUWZheUZFUFBDYkpuRmVnUW9qQTRlTUpKOERpNTgwV250WHZkdTRXUTl2RzVCOGdNR2h4Zkd6ZHBRM2FuZytWMUZQSCtKZjB3T3Z3UlVKV3hKdElDU3hiMHhrTGZJaDJBTzloOFhwekNmbVZVa3pRQnl5MHMwSVkvRGxLSndocW91bVM3c1NRd1dnK3hZeGtEY2FuTTRvSzVJWnZrMUhkZjl4RWhFaEtnWDVCd2c3WHlSYXJPQndsd1FQeHRxeEg0MDg2WXljUnVETWhvQm9kc3IrckRzem5JbHluaVhMcjEvNkRHUDBHNUFPSWMvcS9aeEgwVldrR2RsUngwMVVIYlp4eWh6RzBObm9CQVIySGd1aUNOSkdMay9ROHl1UkFGRnNWTFpkcEJlVEJiR3BVVHI1WTZYREtKOXptS2UzSFF5TTQ5aW1nTVY0Y1gybUcrTHJHVWI0ZG9yQTVId1VzTWs4NWtuWlptSkhxUVFvbDZPKzJKMldDTlRGUFVpV0RiLy9oVzh5VFBJWGxudXJ4Z0hUTXhvY2ZIdG14WkxrTDlsWWx0TWFYMmo5OXhNVlozTWl6RFUyZUFvMEx6aDcyY2s3T3BlelpDd0JHeUNyOU55THdhRC9xR2hCVklCMWQrOVQ5cDczTW5lemU0RytWdGdZNXlLZEhFZnFkMjFuS2k5WEdYRWRUZlMxNXljWUcxUzBXRzU2azIzakxwZG9MMElKZ1ZqUWNMTVdrTUlHdlhUNUlwYzZEMUNUVXFrVnJNZTZuejBmeFpjL3pzbXJhaWJDZUIvUzBOc2JPOXozN2tlS200S01rPSZTZXdwNTRnWHIvV21vNWRiVXdVa1ZOUzB0b0k9'
    p = PinterestSearchImprovement(cookie)
    print(p.get_recommend('light'))

