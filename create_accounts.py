from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from config import PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS, anty_api_key, referral_code
import pyperclip
import string
from time import sleep
import json
import zipfile
import random


manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)


def generate_password():
    length = 12
    lower_case_letters = string.ascii_lowercase
    upper_case_letters = string.ascii_uppercase
    digits = string.digits
    special_characters = string.punctuation

    all_characters = lower_case_letters + upper_case_letters + digits + special_characters

    password = [
        random.choice(lower_case_letters),
        random.choice(upper_case_letters),
        random.choice(digits),
        random.choice(special_characters)
    ]

    password += random.choices(all_characters, k=length - 4)

    random.shuffle(password)

    return ''.join(password)


def acp_api_send_request(driver, message_type, data={}):
    message = {
        # всегда указывается именно этот получатель API сообщения
        'receiver': 'antiCaptchaPlugin',
        # тип запроса, например setOptions
        'type': message_type,
        # мерджим с дополнительными данными
        **data
    }
    # выполняем JS код на странице
    # а именно отправляем сообщение стандартным методом window.postMessage
    return driver.execute_script("""
    return window.postMessage({});
    """.format(json.dumps(message)))


def get_chromedriver():
    options = webdriver.ChromeOptions()

    plugin_file = 'proxy_auth_plugin.zip'
    with zipfile.ZipFile(plugin_file, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    #options.add_extension(plugin_file)

    options.add_extension('anticaptcha-plugin_v0.67.zip')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    return driver


def create_account(driver):
    letters = string.ascii_lowercase
    username = ''.join(random.choice(letters) for i in range(10))
    password = generate_password()

    driver.get('https://app.getgrass.io/register')

    driver.execute_script("window.open('https://mails.org/ru/', '_blank');")

    driver.switch_to.window(driver.window_handles[1])
    sleep(5)

    driver.find_element(by=By.XPATH, value="//*[@class='icon text-muted']").click()
    temp_email = pyperclip.paste()

    sleep(1)
    driver.switch_to.window(driver.window_handles[0])
    driver.refresh()
    sleep(1)
    driver.find_element(by=By.XPATH, value="//*[@placeholder='Email']").send_keys(temp_email)
    sleep(1)
    driver.find_element(by=By.XPATH, value="//*[@placeholder='Username']").send_keys(username)
    sleep(1)
    driver.find_element(by=By.XPATH, value="//*[@placeholder='Password']").send_keys(password)
    sleep(1)
    driver.find_element(by=By.XPATH, value="//*[@placeholder='Confirm Password']").send_keys(password)
    sleep(1)
    driver.find_element(by=By.XPATH, value="//*[@placeholder='Referral Code']").send_keys(referral_code)
    sleep(1)
    driver.find_element(by=By.XPATH, value="//*[@class='chakra-checkbox__control css-i88593']").click()
    WebDriverWait(driver, 180).until(lambda x: x.find_element(by=By.CSS_SELECTOR, value=".antigate_solver.solved"))
    sleep(1)
    driver.find_element(by=By.XPATH, value="//*[@type='submit']").click()
    sleep(30)
    try:
        driver.find_element(by=By.XPATH, value="//*[@class='chakra-button css-1x35aja']").click()
        with open('accounts.txt', 'a') as f:
            f.write(temp_email + ':' + password + '\n')
    except:
        pass

    return driver


def main_creating():

    while True:
        driver = get_chromedriver()
        driver.get('https://www.google.ru/')

        acp_api_send_request(
            driver,
            'setOptions',
            {'options': {'antiCaptchaApiKey': anty_api_key}}
        )

        driver = create_account(driver)
        driver.quit()








