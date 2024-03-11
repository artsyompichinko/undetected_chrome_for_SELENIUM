from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os
import shutil
import tempfile


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

    # Использование прокси через class ProxyExtension, читай докеумент к классу
    proxy = ("proxy_ip", "proxy_port", "login_proxy", "password_proxy")
    proxy_extension = ProxyExtension(*proxy)
    options.add_argument(f"--load-extension={proxy_extension.directory}")

    # альтернативный способ использования прокси
    #options.add_argument(f"--proxy-server={'proxy_ip'}:{'proxy_port'}")

    # Отключает использование среды безопасности (sandbox) в браузере Chrome.
    options.add_argument("--no-sandbox")

    # Введи язык которой будет использоваться в браузере
    b_lang = 'your_language'
    options.add_argument(f"--lang={b_lang}")

    # Отключаем использование графического процессора
    options.add_argument("--disable-gpu")

    # Отключаем автоматический перевод страниц
    options.add_argument("--disable-translate")

    # Отключаем политику Same-Origin Policy
    options.add_argument("--disable-web-security")

    # Отключаем использование /dev/shm
    options.add_argument("--disable-dev-shm-usage")

    # Устанавливаем пользовательский агент (User-Agent)
    user_agent = "ваш_пользовательский_агент"
    options.add_argument(f"user-agent={user_agent}")

    # Отключаем алгоритм плавности для WebRTC
    options.add_argument("--disable-rtc-smoothness-algorithm")

    # Отключаем определенные функции движка браузера Blink, связанные с автоматизацией
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Блок кода для использования профилей GoogleChrome, нужно быть аккуратным. Сильно влияет на другие настройки браузера.
    # Всегда проверяй как настроен на whoer.net или pixelscan.net
    #options.add_argument('--remote-debugging-port=9222')
    #options.add_argument('--allow-profiles-outside-user-dir')
    #options.add_argument('--enable-profile-shortcut-manager')
    #options.add_argument(r'user-data-dir=.\User')
    #options.add_argument('--profile-directory=Default')

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Расширения в формате .crx класть в папку и прописывать путь
    # Расширение отключает webrtc для предотвращения утечки ip
    options.add_extension("your_path/WebRTC Control 0.3.2.0.crx")

    # Расширение позволяет выбрать геолокацию для браузера
    options.add_extension("your_path/Location Guard 2.5.0.0.crx")

    #Добавляем CHOROMEDRIVER кладём в папку актуальную версию и указываем путь
    s = Service('your_path/chromedriver.exe')

    return webdriver.Chrome(service=s, options=options)

if __name__ == "__main__":
    # Создаётся экземпляр браузера
    driver = create_chrome_instance()

    # Добавление time_zone для браузера в формате America/New_York
    time_zone = 'America/New_York'
    tz_params = {'timezoneId': f'{time_zone}'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    #если используешь IPv6 2ip.ru i whoer.net не откроются пожтому выбор пал на яндекс
    driver.get('https://yandex.ru/Internet')
    input('Проверь на сайте настройки браузера и нажми Enter для завершения скрипта')

