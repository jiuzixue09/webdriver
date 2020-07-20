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
            '现代室内设计', '家具', '街头风格', '房屋建筑', '艺术与摄影', '家居装潢', '女性时尚', '厨房设计', '舞会长礼服', '房屋建筑',
            '梦幻房间', '设计'}


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
        return self.driver.find_element_by_css_selector("div > h2, div >h1").text

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
                    logging.info('in welcome page')
                    self.driver.find_element_by_css_selector(
                        'button[aria-label="Next"]').click()  # Welcome to Pinterest!
                else:
                    logging.info('skip welcome page')

                if not self.wait_for_elements("div > h2,div >h1", 5):
                    logging.info('can\'t find tag h2 ...')
                    return
                if is_first_time or '性别' in self.h2() or 'identify' in self.h2():
                    logging.info('in identity page')
                    self.driver.find_element_by_id('female').click()  # '你是如何认同性别的？'
                    sleep(1)
                else:
                    logging.info('skip identity page')

                if is_first_time or '语言' in self.h2() or 'language' in self.h2():
                    logging.info('in language page')
                    self.driver.find_element_by_id('newUserLanguage').send_keys('简体中文')  # '选择语言和国家/地区'
                    sleep(1)
                    self.driver.find_element_by_id('newUserCountry').send_keys('香港 (香港)')
                    sleep(2)
                    self.driver.find_element_by_css_selector('button[type="submit"]').click()
                    sleep(1)
                else:
                    logging.info('skip language page')

                for _ in range(2):
                    self.categorySelect()
                    sleep(1)

                sleep(1)
                self.driver.find_element_by_css_selector('span.deprecatedTextSizeXL,a.GestaltTouchableFocus')

                cookies = self.driver.get_cookies()
                list_cookies = [c['name'] + "=" + c['value'] for c in cookies]
                cookie = ';'.join(list_cookies)
            except Exception as e:
                logging.exception('something wrong')
                raise e

            return cookie

        except InvalidSessionIdException:
            logging.exception('InvalidSessionIdException')
        except MaxRetryError:
            logging.exception('MaxRetryError')
        except NoSuchWindowException:
            logging.exception('NoSuchWindowException')
        except Exception or TimeoutException as e:
            logging.exception('Exception')
            raise e

    def categorySelect(self):
        title = self.h2()
        if '最后一步' in title or '探索的类别' in title or '深入探索' in title:
            logging.info('in category page')
            elements = self.driver.find_elements_by_css_selector('div.XBe.iD5 > div')  # '最后一步！让我们知道你对什么感兴趣'
            for e in elements:
                print(e.text)
                if e.text in focus_on:
                    _ = e.location_once_scrolled_into_view  # should be called without ()
                    # the location_once_scrolled_into_view is a Python property.
                    e.click()
                    sleep(0.1)

            if self.wait_for_elements('button[type="submit"]', 5):
                logging.info('submit')
            else:
                logging.info('can\'t find submit button')
                return
            self.driver.find_element_by_css_selector('button[type="submit"]').click()

    def close(self):
        logging.info('close driver')
        # noinspection PyBroadException
        try:
            self.driver.stop_client()
            self.driver.quit()
        except Exception:
            logging.exception('close driver exception')


PinterestRegister(False, '/opt/google/chrome/chromedriver', True).get_cookie(
    '_auth=1;_b=\"AU4hqevlwUxLI5qRygxhxkH3j1VbABIyh4UVSL+mR91BnKYJ7iuy5dXDSjTSl5+AWrg=\";_pinterest_sess=TWc9PSZpWVBtVWdTeEgzTEVMVkNVZEcrL0dLU0VaZ0NnV3BqejBWWVZkdUY1cmZTeUR3SENtRXBjb3FwQk1FbENKajZYWDE3Z2kwMzRsYmdORmMrZVRzdGtNbm5WTnZPU0UvQm4wZkM1cytFc09OYytGSDBiWFV6UjZKNjUzODc0VWk3c2VlOXNvYXcvVHk4QmZ6YnBoTkp3dnZBcS9jNUl1ODlGdnRwcWtYUE05ZG10VXc4b1lHODdmTnVtM3pHVVFZeElQdm9kV2ZRM1NzU3NrUG5oU1BsMGxtbGJZaVdIZ2ROWXd6M1hZQVNjQ1E0Z1YzVERpMXNnN05VcnBhSGFybmliOWxVY09FYndkMnJBSnFPYUZobjFnNUVhUVBWYnBwcGtVaE5tY2M5bDllbFlBaGg1YnN1dTZKN1YvR3h1UVEzV241UHVyeXBPblY1SjVLSnNUK0Rta1NqaVp3RXM0ZW85ZVo4eUo4SGZWRVlTR0NjZmpUY2xPWk1JSmdYSjlIdFpIZXd0NmlKYzVGYzBiWXI5Y3k1U0twa3ZlcEZXclBNL2c2WmNOMzRyczVaakl5T1Y0aXNxa01vWVNzcmFIcjdOejVFa0Z4Qk10ZFdyY2xZd2RBK3Z4MjQ5S1N3WHhFbE1uSnJ4NThUelJtdUhhMnlIVHRBR1lGbWpsRzlPa3AwNGtzbE8zVEV1QU8vUjBxWk1TWkgyOTZXUUNRMUpoQ2NuVng1QXIzRmJmaGQvRXVwOFRHRDFSeEsvTVZSYWNhdGNRZkFOc2FhOEV3VWgzTTVFZTRQUENpb2xsc2poNGJPLzhiMWV3NGE3dXlJOFlpMEZtWTlidjVnNTdhZGdHOW0xMU93blVGZ01IakZxQXRaa2poT3ZHYVlWejBlOGduNEkydFp3MElxdFpyL0pQcFU5YlQzb1VPcVJraHFwV0VVQUZDMS9HODVlVkdZMEJnVW9WWW5HVUhsZ1JKaUdicHBNdnRaM2llY2FHUkR4VDBUcURCNHhSaU5DcVI2aHdkS1hmY3h1b2c3YmVEVEs3OE13RXlRN21EZGp2Zjc1a2duWVdISWxIdzdVQWI5UmRLd3B3QkRFRDU1cFRXUnZ2aGIvL2hWT3RoUzc2cW5sbnFUR1l0TmRqOFZkZUt0MUVja0J1UVJSOHpCUWRsc0RVNW41OURUWFlDL2YwcmtSSUxKZXdNQ0NSRGRxOWs1b1piTGZhUXlhV2hLc1NYaGlTdzFTY2hKS25Wdmc2a21aYkJpd1lNQ0c4bExiMWpaQnYrbmlnMWZGQ0JvdUdtL1JkbXRTWisyVlNqR0JLNEVvbXJQdzZLRWV2b3Y2K3p6TDVENWNvYlFWMllZeWVXNnBSWFNHdDdtT0JDL3ZwUEhFL1dEOWE2akZ6Zz09JktEdXVVTVFWamVFcTlVUzRKVExFaktWdmZTcz0=')
