import json
import random
import string

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from time import sleep
from mail import get_code, get_email


anty_api_key = '86fab685c1b83c34e38c1f2903d5a62e'

def browser_click_element(driver, value):
    button = driver.find_element(by=By.XPATH, value=value)
    driver.execute_script(
        "var evt = document.createEvent('MouseEvents'); "
        "evt.initEvent('click', true, true); arguments[0].dispatchEvent(evt);",
        button)


def browser_click_elements(driver, n, value):
    button = driver.find_elements(by=By.XPATH, value=value)[n]
    driver.execute_script(
        "var evt = document.createEvent('MouseEvents'); "
        "evt.initEvent('click', true, true); arguments[0].dispatchEvent(evt);",
        button)

def acp_api_send_request(driver, message_type, data={}):
    message = {
        'receiver': 'antiCaptchaPlugin',
        'type': message_type,
        **data
    }
    return driver.execute_script("""
    return window.postMessage({});
    """.format(json.dumps(message)))

def create_account():
    options = webdriver.ChromeOptions()
    options.add_extension('anticaptcha-plugin_v0.67.zip')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get('https://www.google.ru/')
    acp_api_send_request(
                driver,
                'setOptions',
                {'options': {'antiCaptchaApiKey': anty_api_key}}
            )
    driver.get('https://war.day/?ref=4Khy6r')
    sleep(2)
    browser_click_elements(driver, 11, value="//*[@class='nav__item']")
    sleep(2)
    browser_click_element(driver, value="//*[@class='ml-1 btn']")
    sleep(2)

    temp_email = get_email()
    driver.find_element(by=By.XPATH, value="//*[@id='email']").send_keys(temp_email)
    sleep(1)

    letters = string.ascii_lowercase
    driver.find_element(by=By.XPATH, value="//*[@id='nick']").send_keys(''.join(random.choice(letters) for _ in range(10)))
    sleep(1)
    password = ''.join(random.choice(letters) for _ in range(10))
    driver.find_element(by=By.XPATH, value="//*[@id='password']").send_keys(password)
    sleep(1)
    driver.find_element(by=By.XPATH, value="//*[@id='password-confirm']").send_keys(password)
    sleep(1)
    browser_click_element(driver, value="//*[@class='min-w-0']")
    sleep(1)
    WebDriverWait(driver, 180).until(lambda x: x.find_element(by=By.CSS_SELECTOR, value=".antigate_solver.solved"))

    browser_click_element(driver, value="//*[@class='btn btn-lg mt-6 align-self-start p-0']")

    sleep(3)

    driver.close()


def start():
    while True:
        try:
            create_account()
        except:
            pass