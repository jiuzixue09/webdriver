import requests
import json
from pinterest import LoggingUtil

logging = LoggingUtil.get_logging()


request_url = 'https://www.pinterest.com/resource/UserSessionResource/create/'


class PinterestLogin:

    @staticmethod
    def __get_headers():
        headers = {
            'x-pinterest-appstate': 'active',
            'x-app-version': '35d3566',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded',
            'x-pinterest-experimenthash': 'f5ed47c46929fb64d93c31b772f194fbf884c01a3c7ff5444a68390db7bea177980411a0e6c929d5760d43b783db9355b01b93e766a8752904e95dde3dafd84d',
            'x-csrftoken': 'fdb48c9784a30c1478142ace8fa936c9',
            'origin': 'https://www.pinterest.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': 'https://www.pinterest.com/',
            'cookie': '_routing_id="438d48e0-3f4f-496e-a7c2-1171e2fb6d7e"; csrftoken=fdb48c9784a30c1478142ace8fa936c9; sessionFunnelEventLogged=1; G_ENABLED_IDPS=google; bei=false; cm_sub=none; logged_out=True; _auth=0; fba=True; _pinterest_sess=TWc9PSZIT3lHOThNQmF1QlJmUEd3M0FtZjF4YkJMUFJHUjZYSVd0NHhuQ3Y1dWdLdDZhRTBpYzBaSFZZT2xoTVREWnZhNW1DMHFNcmVYWWp0d3NObnovSmFLVmRpNy9VRmlUcStEUHFPejhmNENqTkx1ejBWckJPZG1LeGV0NFBQVjJ0dVFsSXF1cFBpZDlScER2Q1VUTXZHazFsMGtFSnlrd1p6dkovV1VRQWYrbXNPVU5vNnY2emIrbFRkaHpmMHdGV0VuSFZSalBDbmkxekpPcGNPc3dITmw5TWdqYlRtTlhROVlLMnQ0Y0swYXhibTVnU0thSEtsY2FaNnhPVkdJYnNJN2Y3ZnQ0dXZxdzhhdlFXTjVhcW5zTkxtVWgwNUxTSUhSODhqTXRRODJqV0xVUXRJT2VoRUdPUWhVWUt4aEhIVmE0cERuT3c4Vm1LaHF6dUxJdkVQa1JTZU94R3VVTkRQOG12TFIzY2czVG89Jld6UVNoa0YvODV0THJ2c3dFSVNsengxc1Q3ST0=',
            }
        return headers

    @staticmethod
    def __get_params(user_name, password):
        params = {
            'source_url': '/',
            'data': '{"options":{"username_or_email":"' + user_name + '","password":"' + password + '",'
            '"app_type_from_client":5,"visited_pages_before_login":null,"tokenV3":"default"},"context":{}}'
        }
        return params

    def __init__(self):
        super().__init__()
        self.headers = self.__get_headers()

    def get_cookie(self, user_name, password, proxies=None):
        status_code = 0
        str_cookie = ''
        try:
            response = requests.post(request_url, proxies=proxies, headers=self.headers, data=self.__get_params(user_name, password))
            status_code = response.status_code
            if status_code == 401:
                content = response.content.decode("utf-8")
                j = json.loads(content)
                message_detail = j['resource_response']['error']['message_detail']
                logging.info("user_name=%s, password=%s, status=%s, message_detail=%s", user_name, password, status_code, message_detail)
            else:
                logging.info("user_name=%s, password=%s, status=%s", user_name, password, status_code)
                try:
                    list_cookies = [c.name + '=' + c.value for c in response.cookies]
                    str_cookie = ';'.join(list_cookies)
                except Exception as e:
                    logging.exception('user_name=%s, password=%s', user_name, password)
        except Exception as e:
            logging.exception('user_name=%s, password=%s', user_name, password)
        finally:
            return status_code, str_cookie


# if __name__ == '__main__':
#     p = PinterestLogin()
#     proxies = {
#         'http': 'http://127.0.0.1:7890',
#         'https': 'http://127.0.0.1:7890',
#     }
#     print(p.get_cookie('usnruaaj@163.com', '123456-- asdf', proxies))

