
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, InvalidSessionIdException, NoSuchWindowException
from selenium.webdriver.chrome.options import Options
from urllib3.exceptions import MaxRetryError
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from pinterest import LoggingUtil

logging = LoggingUtil.get_logging('webdriver_module')


focus_on = {'家居装潢', '时尚', '艺术', '绘画', '壁纸', '穿搭', '摄影', '设计', '休闲穿搭', '旅行', '梦幻房间', '动漫', '漫画', '动画', '艺术与工艺品',
            '现代室内设计', '家具', '街头风格', '房屋建筑'}


class PinterestRegister:
    def __init__(self, headless, chrome_driver, proxy=False):
        super().__init__()

        options = Options()
        if headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')

        logging.info('chrome_driver=%s', chrome_driver)
        if proxy:
            proxy = '127.0.0.1:7891'
            options.add_argument('--proxy-server=socks5://' + proxy)

        self.driver = webdriver.Chrome(options=options
                                       , executable_path=chrome_driver)

        # self.driver.set_page_load_timeout(20)
        self.set_window_size()
        self.driver.set_script_timeout(20)
        self.driver.implicitly_wait(10)
        self.url = 'https://www.pinterest.com'

    def wait_for_elements(self, css_select, timeout=10):
        # noinspection PyBroadException
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_select)))
            return True
        except Exception:
            logging.exception('can\'t find elements:{}'.format(css_select))
            return False

    def set_window_size(self):
        self.driver.set_window_size(1024, 768)

    def h2(self):
        return self.driver.find_element_by_css_selector("div > h2").text

    def delete_all_cookies(self):
        self.driver.delete_all_cookies()

    def get_cookie(self, str_cookie: str):
        try:
            self.driver.get('https://www.baidu.com')

            for c in str_cookie.split(';'):
                kv = c.split("=", 1)
                k, v = kv[0], kv[1]
                self.driver.add_cookie({'name': k, 'value': v, 'domain': 'pinterest.com'})

            self.driver.get(self.url)

            try:
                is_first_time = self.wait_for_elements('button[aria-label="Next"]', 5)
                if is_first_time:
                    self.driver.find_element_by_css_selector(
                        'button[aria-label="Next"]').click()  # Welcome to Pinterest!

                if not self.wait_for_elements("div > h2", 5):
                    logging.info('can\'t find tag h2 ...')
                    return
                if is_first_time or '性别' in self.h2() or 'identify' in self.h2():
                    self.driver.find_element_by_id('female').click()  # '你是如何认同性别的？'
                    sleep(1)

                if is_first_time or '语言' in self.h2() or 'language' in self.h2():
                    self.driver.find_element_by_id('newUserLanguage').send_keys('简体中文')  # '选择语言和国家/地区'
                    sleep(1)
                    self.driver.find_element_by_id('newUserCountry').send_keys('香港 (香港)')
                    sleep(1)
                    self.driver.find_element_by_css_selector('button[type="submit"]').click()
                    sleep(1)

                if is_first_time or '最后一步' in self.h2():
                    elements = self.driver.find_elements_by_css_selector('div.XBe.iD5 > div')  # '最后一步！让我们知道你对什么感兴趣'
                    for e in elements:
                        print(e.text)
                        if e.text in focus_on:
                            e.location_once_scrolled_into_view # should be called without ()
                            # the location_once_scrolled_into_view is a Python property.
                            e.click()
                            sleep(0.1)

                self.driver.find_element_by_css_selector('button[type="submit"]').click()

                self.driver.find_element_by_css_selector('span.deprecatedTextSizeXL')

                cookies = self.driver.get_cookies()
                list_cookies = [c['name'] + "=" + c['value'] for c in cookies]
                cookie = ';'.join(list_cookies)
            except Exception as e:
                logging.exception('something wrong')
                raise e

            return cookie

        except InvalidSessionIdException as e:
            logging.exception('InvalidSessionIdException')
        except MaxRetryError as e:
            logging.exception('MaxRetryError')
        except NoSuchWindowException as e:
            logging.exception('NoSuchWindowException')
        except Exception or TimeoutException as e:
            logging.exception('Exception')
            raise e

    def close(self):
        logging.info('close driver')
        # noinspection PyBroadException
        try:
            self.driver.stop_client()
            self.driver.quit()
        except Exception:
            logging.exception('close driver exception')


PinterestRegister(False, '/opt/google/chrome/chromedriver', True).get_cookie('_auth=1;_b="AU43zUxu3a1Fa6sfIOD0fv+Zlfg2dKMNQdQn8cTgWzlvsJn3OanjhXW8RHIFcmjegJM=";_pinterest_sess=TWc9PSZleEIzRTJrd0I0dVAySnJjQ2xSZHZWYUJodU45TDl4cktvQVZ0MGpCQlRjaXBjdTkzN253RmhSYlExWGNsU1hVeXB5bVd0bExwekJUTmYyVkI3K3VkWGEyRHhzNWorZHQ3YzIzNHNta2dQNkJDT3BjS2MvZG01TUk3Q0hKTUJzdTVWbnZRRytaZjIvVHFXdUsvQ1VYbWROc3BESTV3WmFvTUgyWVEvKzlwelZ3cE1yMG41eTRtSmJaeUNYNnlTM2VJaHNaS0VtTE9NdUswbStVTmo0Y0ExQVdSUXlteDF3c2RJQU53bHYwNVozZVRjZUlPQWx4dXlpR1B6UE9xbGRDc09qNjZKVy9PWUpmRlQwZ3EvZTAxR1lUN0grcWM0SlRRZG5FVEhDbTZtOTRLOTBneEI2aTFxUVVuNkUzdzNXODErTm5DejQrMndkMGp3cmpNOUxDdnIwSkIwbm1XanlVa3EvMDBCYnBHbi96VFlRbUMrdEJGQ0cyM0dnVlBzTEFXSXp6UzRkYThzUHc4OUpPSFpnMmI5Z2p0K3ZuWCttaU0xNHhqZ2l5aXB1Wnp0bFhPWFNNa1VuWWhBdFlmblpYUEZCeHV6ZmJySUcwK21CMlllVFdYb0NxRmxZQzdXNkhuNS82NGVsb2s1ZmVpWTRidWIwSGRkTUtnUEh3Yzdod0VOLy9rd1lLMXhZN3dGRnVFVTYycHhxY2drL3E0aEdLY3VKVnU4SHZKcVFTZ3VxbTNLTjBZbzFoZ0NzbU5RZG1MSEVQNHV1K3Vpb2FkdmJ4emRiSk45dVJDSUx5bTRDYkVZcC8yMUNmUjZNOGMzM3hqSE9la3RxYk9JWC9xRjg0NW9zMlorSW94dzA1bjNHZ0VDcWJoSFJIR211dTFaRVhPRHNhZzlINm14V3l0RXBoY3JMUW1ZOHROWStJSHl1Wk1zblFxdC9JYTB3WFdLT0ZZZnZCMEtBZlczdUJnZ2VPYWRJS0taMlVaOVNNMldXbkpLWmlZSUxHdXF2cWhUdWdNTGRFaGppNGh6czJraUt2ZmxJaGRoenhGcmNHNWhaVWVDRXB5dzhOQ1plbXdZOENvWVBGQ1cxVTV5MFdZNE95TzkrdmRjVnFESU8vYTVNdzM0cUJNZDltQTVBa3J4TXFqaTYxdWQra0d6YVRzN2ZlYmpoNnp6bG8rTmNIb3JnaVdzOEtlWUdIQTJkZ3MweWxnVW91MEJXcjhnanlwdTNmSFFPdWo2dStzSk4vWWlGNTlZOUZXN2U5ekRVZ2dweHpRd2lJM0FGMFVrY011OHVFMXF1MEh4WnRhTm9uWUJRek1hUkZvNW9laUpRdTliL3BQTDdIZkpRRFpiUHpEdENIcEZlSzlZaFpPSnUvejAvSzNQaFdCUT09JlowelRERk42QnIvRDVSTjdTL0xXeExrVy8rRT0=')
