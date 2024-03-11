from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import login_data as dfcb
import pickle
import time
import random
import os
import shutil
import tempfile
from datetime import datetime

class ProxyExtension:
    '''Авторизация прокси для Undetected_chromedriver. По сути это расширение для chrome.
    Не всегда работает коректно, рекомендую проверять на 2ip.ru.
    В функции create_chrome_instance закоментирован второй способ подключения прокси.'''

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
        "background": {"scripts": ["background.js"]},
        "minimum_chrome_version": "76.0.0"
    }
    """

    background_js = """
    var config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: %d
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
        { urls: ["<all_urls>"] },
        ['blocking']
    );
    """

    def __init__(self, host, port, user, password):
        self._dir = os.path.normpath(tempfile.mkdtemp())

        manifest_file = os.path.join(self._dir, "manifest.json")
        with open(manifest_file, mode="w") as f:
            f.write(self.manifest_json)

        background_js = self.background_js % (host, port, user, password)
        background_file = os.path.join(self._dir, "background.js")
        with open(background_file, mode="w") as f:
            f.write(background_js)

    @property
    def directory(self):
        return self._dir

    def __del__(self):
        shutil.rmtree(self._dir)



def create_chrome_instance():
    '''Создание экземпляра браузера Googlechrome'''
    options = webdriver.ChromeOptions()
    proxy = (dfcb.proxy_ip, dfcb.proxy_port, dfcb.login_proxy, dfcb.password_proxy)
    proxy_extension = ProxyExtension(*proxy)
    options.add_argument(f"--load-extension={proxy_extension.directory}")
    options.add_argument(f"--proxy-server={dfcb.proxy_ip}:{dfcb.proxy_port}")
    options.add_argument(f"--proxy-auth={dfcb.login_proxy}:{dfcb.password_proxy}")
    options.add_argument("--no-sandbox")
    options.add_argument(f"--lang={dfcb.language}")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-translate")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f'user-agent={dfcb.user_agent}')
    options.add_argument("--disable-rtc-smoothness-algorithm")
    options.add_argument("--disable-blink-features=AutomationControlled")

    #options.add_argument('--remote-debugging-port=9222')
    #options.add_argument('--allow-profiles-outside-user-dir')
    #options.add_argument('--enable-profile-shortcut-manager')
    #options.add_argument(r'user-data-dir=.\User')
    #options.add_argument('--profile-directory=Default')

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_extension("WebRTC Control 0.3.2.0.crx")
    options.add_extension("Location Guard 2.5.0.0.crx")

    s = Service('chromedriver.exe')
    return webdriver.Chrome(service=s, options=options)