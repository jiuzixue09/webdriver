from io import BytesIO
from time import sleep

from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def scroll_down(driver):
    driver.execute_script("""
           (function () {
               var y = 0;
               var step = 100;
               window.scroll(0, 0);

               function f() {
                   if (y < document.body.scrollHeight) {
                       y += step;
                       window.scroll(0, y);
                       setTimeout(f, 100);
                   } else {
                       window.scroll(0, 0);
                       document.title += "scroll-done";
                   }
               }

               setTimeout(f, 1000);
           })();
       """)

    for i in range(30):
        if "scroll-done" in driver.title:
            break
        sleep(1)
    driver.execute_script('window.scrollTo(0, 0);')


def full_screenshot(driver, save_path):
    # initiate value
    save_path = save_path + '.png' if save_path[-4::] != '.png' else save_path
    img_li = []  # to store image fragment
    offset = 0  # where to start

    # js to get height
    height = driver.execute_script('return Math.max('
                                   'document.documentElement.clientHeight, window.innerHeight);')

    # js to get the maximum scroll height
    # Ref--> https://stackoverflow.com/questions/17688595/finding-the-maximum-scroll-position-of-a-page
    max_window_height = driver.execute_script('return Math.max('
                                              'document.body.scrollHeight, '
                                              'document.body.offsetHeight, '
                                              'document.documentElement.clientHeight, '
                                              'document.documentElement.scrollHeight, '
                                              'document.documentElement.offsetHeight);')

    # looping from top to bottom, append to img list
    # Ref--> https://gist.github.com/fabtho/13e4a2e7cfbfde671b8fa81bbe9359fb
    n = max_window_height // height
    for i in range(n):
        sleep(.5)
        # Scroll to height
        driver.execute_script(f'window.scrollTo(0, {offset});')
        img = Image.open(BytesIO((driver.get_screenshot_as_png())))

        img_li.append(img)
        offset += height

    # Stitch image into one
    # Set up the full screen frame
    img_frame_height = sum([img_frag.size[1] for img_frag in img_li])
    img_frame = Image.new('RGB', (img_li[0].size[0], img_frame_height))
    offset = 0
    for img_frag in img_li:
        img_frame.paste(img_frag, (0, offset))
        offset += img_frag.size[1]
    img_frame.save(save_path)


def taobao_full_screenshot(driver, save_path):
    scroll_down(driver)
    driver.execute_script("document.getElementById('J_TabBarWrap').remove()")
    # driver.execute_script('document.getElementById("sufei-dialog-close").click()')
    full_screenshot(driver, save_path)


def bigbigwork_full_screenshot(driver, save_path):
    driver.execute_script("document.getElementsByClassName('header')[0].remove()")
    driver.execute_script("document.getElementsByClassName('pinterestbox')[0].remove()")
    full_screenshot(driver, save_path)


chromedriver = r"/opt/google/chrome/chromedriver"
str_cookie = ''
options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument("disable-infobars")
options.add_argument("--disable-notifications")

options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(options=options, executable_path=chromedriver)


driver.maximize_window()

''' Generate document-height screenshot '''
url = "https://www.bigbigwork.com/"
driver.get(url)
for c in str_cookie.split(';'):
    kv = c.split("=", 1)
    k, v = kv[0], kv[1]
    driver.add_cookie({'name': k.strip(), 'value': v, 'domain': 'taobao.com'})

url = 'https://item.taobao.com/item.htm?spm=a219r.lm874.14.26.3b2f4ec5MsSl3w&id=615753578371&ns=1&abbucket=18'
driver.set_script_timeout(20)
driver.implicitly_wait(10)
driver.get(url)
driver.maximize_window()
taobao_full_screenshot(driver, "test1235.png")
driver.close()
