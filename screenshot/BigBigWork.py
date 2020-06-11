import os
import time
from time import sleep

import yaml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from screenshot import LoggingUtil

logging = LoggingUtil.get_logging()

with open('config.yaml') as file:
    logging.info('读取配置文件： config.yaml')
    config = yaml.safe_load(file.read())


class BigBigWork:

    def wait_for_elements(self, css_select, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_select)))
            return True
        except Exception as e:
            logging.exception('can\'t find elements:{}'.format(css_select))
            return False

    def __init__(self, headless=False, root=None, change_user_state_url=None, home_url=None, login_url=None, env=None):

        logging.info("初始化浏览器")
        options = Options()
        if headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')

        chromedriver = r"/opt/google/chrome/chromedriver"
        logging.info('chromedriver=%s', chromedriver)

        self.driver = webdriver.Chrome(options=options
                                       , executable_path=(r"%s" % chromedriver))
        # self.driver.maximize_window()
        self.driver.set_page_load_timeout(20)
        self.driver.set_script_timeout(20)
        self.driver.implicitly_wait(20)

        self.change_user_state_url = change_user_state_url
        self.login_url = login_url
        self.home_url = home_url

        path = time.strftime('%Y%m%d%H%M')
        if root is not None:
            path = path + '/' + root
        if env is not None:
            path = env + '/' + path
        self.path = path

        if not os.path.exists(path):
            os.makedirs(path)

    def get_path(self):
        return self.path

    def change_login_times(self, times):
        url = self.change_user_state_url.format(times, times)
        self.driver.get(url)

    def open(self, url):
        logging.info("打开页面, %s", url)
        self.driver.get(url)

    def login(self, user_name, user_password, times):
        self.open(self.login_url)
        logging.info("用户第%d次登录，用户名=%s, 密码=%s", times, user_name, user_password)
        self.driver.find_element_by_css_selector('div.login.btn').click()
        self.driver.find_element_by_css_selector('div.weixin-login-toPhone > a > i').click()
        self.driver.find_element_by_css_selector('ul.inputbox li input[type=text]').send_keys(user_name)
        self.driver.find_element_by_css_selector('ul.inputbox li input[type=password]').send_keys(user_password)
        self.driver.find_element_by_css_selector('button.loginbutton').click()
        time.sleep(1)
        if self.driver.current_url != self.home_url:
            try:
                if self.wait_for_elements('span._tip', 5):
                    txt = self.driver.find_element_by_css_selector('span._tip').text
                    if len(txt) > 0:
                        logging.exception('%s', txt)
                        self.save(self.path + '/' + str(times) + '登_失败' + '.png')
                        return txt
            except Exception as e:
                logging.exception('login error')
                self.save(self.path + '/' + str(times) + '登_失败' + '.png')
        return None

    def set_window_size(self):
        self.driver.set_window_size(1024, 768)

    def screen_shot(self, times=0):
        try:
            logging.info("截图，图片目录=%s", self.path)
            if self.wait_for_elements('div.gift-content'):
                gift = self.driver.find_element_by_css_selector('div.gift-content')
                sleep(1)
                self.save(self.path + '/' + str(times) + '登_gift' + '.png')
                gift.click()

                self.driver.switch_to.window(self.driver.window_handles[-1])

                containers = self.driver.find_elements_by_css_selector('div.container-center > div')
                for i in range(len(containers)):
                    containers[i].click()
                    sleep(1)
                    self.save(self.path + '/' + str(times) + '登_payment_' + str(i) + '.png')
            else:
                self.save(self.path + '/' + str(times) + '登_无gift' + '.png')
        except Exception as e:
            logging.exception('截图异常')

    def screen_shot2(self, times=0):
        try:
            self.open(self.home_url)
            sleep(1)

            self.wait_for_elements('#p-button')
            self.driver.find_element_by_id("p-button").click()
            items = self.driver.find_elements_by_css_selector('#VIPSelect > li.item')

            for i in range(len(items)):
                items[i].click()
                sleep(1)
                self.save(self.path + '/' + str(times) + '登_下载_' + str(i) + '.png')

            sleep(0.5)
            self.driver.execute_script('document.getElementsByClassName("closedthismask")[0].click()')
            sleep(0.5)
            self.save(self.path + '/' + str(times) + '登_下载_' + str(len(items)) + '.png')
        except Exception as e:
            logging.exception('截图异常')

    def save(self, name):
        # self.driver.set_window_size(2048, 1536)
        self.set_window_size()

        # self.driver.execute_script("document.body.style.zoom='200%'")
        element_png = self.driver.get_screenshot_as_png()
        with open(name, "wb") as file:
            file.write(element_png)

    def close(self):
        logging.info("关闭浏览器")
        self.driver.quit()

    def login_out(self):
        page_url = 'http://p.bigbigwork.com/login-out.htm?redirect=www'
        self.driver.get(page_url)
        if len(self.driver.window_handles) > 1:
            self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def delete_all_cookies(self):
        self.driver.delete_all_cookies()
        if len(self.driver.window_handles) > 1:
            self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])


def normal_user_test(env):
    rs = {'status': 'ok'}
    configuration = config.get(env)
    login_url = configuration.get('login_url')
    change_user_state_url = configuration.get('change_user_state_url')
    home_url = configuration.get('home_url')
    normal_user = configuration.get('account').get('normal_user')
    user_name = str(normal_user.get('name'))
    password = str(normal_user.get('password'))

    hide_browser = True if normal_user.get('hide_browser') == 1 else False

    big_big_work = path = None
    try:
        big_big_work = BigBigWork(hide_browser, user_name, change_user_state_url, home_url, login_url, env)
        for i in range(normal_user.get('login_times') + 1):
            info = big_big_work.login(user_name, password, i)
            if info is not None:
                rs['status'] = 'error'
                rs['reason'] = info
                return rs
            if i > 0:
                big_big_work.screen_shot(i)
                big_big_work.screen_shot2(i)
            time.sleep(1)
            big_big_work.change_login_times(i + 1)
            big_big_work.delete_all_cookies()
            path = big_big_work.get_path()
    except Exception as e:
        rs['status'] = 'error'
        rs['reason'] = '页面加载异常'
        logging.exception('normal user screenshot error')

    finally:
        big_big_work.close()

    rs['user_path'] = path
    abspath = os.path.abspath(os.path.dirname(path))
    rs['path'] = abspath
    return rs


def vip_user_test(env):
    rs = {'status': 'ok'}
    configuration = config.get(env)
    login_url = configuration.get('login_url')
    change_user_state_url = configuration.get('change_user_state_url')
    home_url = configuration.get('home_url')
    vip_user = configuration.get('account').get('vip_user')
    user_name = str(vip_user.get('name'))
    password = str(vip_user.get('password'))

    hide_browser = True if vip_user.get('hide_browser') == 1 else False

    path = big_big_work = None
    try:
        big_big_work = BigBigWork(hide_browser, user_name, change_user_state_url, home_url, login_url, env)
        for i in range(vip_user.get('login_times') + 1):
            info = big_big_work.login(user_name, password, i)
            if info is not None:
                rs['status'] = 'error'
                rs['reason'] = info
                return rs
            if i > 0:
                big_big_work.screen_shot(i)
            time.sleep(1)
            big_big_work.change_login_times(i + 1)
            big_big_work.delete_all_cookies()
            path = big_big_work.get_path()
    except Exception as e:
        logging.exception('vip user screenshot error')
    finally:
        rs['status'] = 'error'
        rs['reason'] = '页面加载异常'
        big_big_work.close()

    rs['user_path'] = path
    abspath = os.path.abspath(os.path.dirname(path))
    rs['path'] = abspath
    return rs


# normal_user_test('prod')

# pip3 install selenium pyyaml

