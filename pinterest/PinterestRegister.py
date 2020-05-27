
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, InvalidSessionIdException, NoSuchWindowException
from selenium.webdriver.chrome.options import Options
from urllib3.exceptions import MaxRetryError

from pinterest import LoggingUtil

logging = LoggingUtil.get_logging('webdriver_module')


focus_on = {'家居装潢', '时尚', '艺术', '绘画', '壁纸', '穿搭', '摄影', '设计', '休闲穿搭', '旅行', '梦幻房间', '动漫', '漫画', '动画', '艺术与工艺品',
            '现代室内设计', '家具', '街头风格', '房屋建筑'}


class PinterestRegister:
    def __init__(self, headless, chrome_driver):
        super().__init__()

        options = Options()
        if headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')

        logging.info('chrome_driver=%s', chrome_driver)

        self.driver = webdriver.Chrome(options=options
                                       , executable_path=chrome_driver)

        # self.driver.set_page_load_timeout(20)
        self.driver.set_script_timeout(20)
        self.driver.implicitly_wait(10)
        self.url = 'https://www.pinterest.com'

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
                is_first_time = True
                try:
                    self.driver.find_element_by_css_selector(
                        'button[aria-label="Next"]').click()  # Welcome to Pinterest!
                    sleep(1)
                except Exception as e:
                    logging.error('can\'t find next button', e)
                    is_first_time = False

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
                        if e.text in focus_on:
                            print(e.text)
                            e.click()
                            sleep(0.1)

                self.driver.find_element_by_css_selector('button[type="submit"]').click()

                self.driver.find_element_by_css_selector('span.deprecatedTextSizeXL')

                cookies = self.driver.get_cookies()
                list_cookies = [c['name'] + "=" + c['value'] for c in cookies]
                cookie = ';'.join(list_cookies)
            except Exception as e:
                logging.error('something wrong', e)
                raise e

            return cookie

        except InvalidSessionIdException as e:
            logging.error('InvalidSessionIdException', e)
        except MaxRetryError as e:
            logging.error('MaxRetryError', e)
        except NoSuchWindowException as e:
            logging.error('NoSuchWindowException', e)
        except Exception or TimeoutException as e:
            logging.error('Exception', e)
            raise e

    def close(self):
        logging.info('close driver')
        try:
            self.driver.stop_client()
            self.driver.quit()
        except Exception as e:
            logging.error('close driver exception', e)
