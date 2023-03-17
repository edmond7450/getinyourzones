import os.path
import requests
import time

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from sys import platform
from webdriver_manager.chrome import ChromeDriverManager

from my_settings import *

BASE_URL = 'https://getinyourzones.com/'


def login(driver):
    driver.get(BASE_URL)
    time.sleep(1)
    try:
        WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/sign_in"]')))
    except:
        return

    try:
        driver.find_element(By.XPATH, '//a[@href="/sign_in"]').click()
        time.sleep(1)

        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//input[@data-test="input-email"]')))
        ele_email = driver.find_element(By.XPATH, '//input[@data-test="input-email"]')
        ele_email.click()
        ele_email.clear()
        ele_email.send_keys(USERNAME)
        time.sleep(1)
        ele_password = driver.find_element(By.XPATH, '//input[@data-test="input-password"]')
        ele_password.click()
        ele_password.clear()
        ele_password.send_keys(PASSWORD)
        time.sleep(1)

        ele_password.send_keys(Keys.ENTER)
        time.sleep(3)

        if 'https://getinyourzones.com/catalog' in driver.current_url:
            return True

    except Exception as e:
        print(repr(e))

    return False


def get_urls(driver):
    start = True
    while True:
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@class="top_menu"]')))
        except:
            pass

        category_urls = []
        categories = []
        ele_categories = driver.find_elements(By.XPATH, '//*[@class="top_menu"]//a')
        for ele_category in ele_categories:
            category_url = ele_category.get_attribute('href')
            # if category_url and category_url not in category_urls and (category_url.find('/categories/') > 0 or category_url.find('/catalog/') > 0):
            if category_url and category_url not in category_urls and category_url.find('/catalog/') > 0:
                category_urls.append(category_url)
                category = ele_category.get_attribute('text').strip()
                categories.append([category, category_url])

        for category, category_url in categories:
            driver.get(category_url)
            try:
                last_height = driver.execute_script("return document.body.scrollHeight")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                new_height = driver.execute_script("return document.body.scrollHeight")

                while new_height != last_height:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(3)
                    last_height = new_height
                    new_height = driver.execute_script("return document.body.scrollHeight")
            except:
                break

            contents = []
            if category_url.find('/categories/') > 0:
                results = driver.find_elements(By.XPATH, '//*[@id="category_content"]/div')
            elif category_url.find('/catalog/') > 0:
                results = driver.find_elements(By.XPATH, '//*[@id="catalog_content"]/div')
            else:
                results = []
            for result in results:
                data_card = result.get_attribute('data-card')
                if data_card.find('collection') > -1:
                    card_type = 'collection'
                elif data_card.find('video') > -1:
                    card_type = 'video'
                else:
                    card_type = ''

                ele_card = result.find_element(By.XPATH, './/a[@class="card-title"]')
                card_title = ele_card.text
                card_url = ele_card.get_attribute('href')

                contents.append([card_type, card_title, card_url])

            for card_type, card_title, card_url in contents:
                if card_type == 'collection':
                    driver.get(card_url)
                    time.sleep(3)

                    items = driver.find_elements(By.XPATH, '//*[@data-area="chapters"]//a[contains(@href, "/programs/")]')
                    for item in items:
                        sub_title = item.find_element(By.XPATH, './/*[@data-area="title"]').text
                        url = item.get_attribute('href')

                        if start == True:
                            mode = 'w'
                            start = False
                        else:
                            mode = 'a+'

                        with open('video_urls.csv', mode, encoding='utf-8') as of:
                            of.write(','.join([category, card_title, sub_title, url]) + '\n')

                else:
                    if start == True:
                        mode = 'w'
                        start = False
                    else:
                        mode = 'a+'

                    with open('video_urls.csv', mode, encoding='utf-8') as of:
                        of.write(','.join([category, card_title, '', card_url]) + '\n')


def main():
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument("window-size=1250,1000")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--no-sandbox")
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        chrome_options.add_argument(f'Upgrade-Insecure-Requests=1')
        chrome_options.add_argument(f'user-agent={user_agent}')
        chrome_options.add_argument('--verbose')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')

        if platform == "win32" or platform == "win64":
            data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'selenium')
            chrome_options.add_argument(f"--user-data-dir={data_dir}")
            # chrome_options.add_argument("--headless")

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

        print("Start! : " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
        time.sleep(1)

        login(driver)

        get_urls(driver)

        driver.close()
        driver.quit()
        driver = None

    except Exception as e:
        print(repr(e))
        if driver:
            driver.close()
            driver.quit()

    print("End! : " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))


if __name__ == "__main__":
    if platform == "linux" or platform == "linux2":
        display = Display(visible=0, size=(1250, 1000))
        display.start()

    main()

    if platform == 'linux' or platform == 'linux2':
        display.stop()

    exit(1)