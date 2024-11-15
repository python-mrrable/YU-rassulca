import time
import random
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
import logging
import os
from utils import load_file_content, load_xlsx_content, get_random_line, save_file_content

# Настройка логирования
logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='a')

from fake_useragent import UserAgent
import random

def create_driver(proxy):
    options = Options()
    ua = UserAgent()  # Создаем объект UserAgent
    user_agent = ua.random  # Генерация случайного user-agent
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference('useAutomationExtension', False)
    options.set_preference("general.useragent.override", user_agent)  # Установка уникального user-agent

    # Создаем Firefox профиль
    profile = webdriver.FirefoxProfile()
    profile.set_preference("intl.accept_languages", "en-US, en")
    profile.set_preference("network.http.accept-encoding", "gzip, deflate")
    profile.set_preference("network.http.connection", "keep-alive")
    profile.set_preference("network.http.referer.spoofSource", True)
    profile.set_preference("network.http.sendRefererHeader", 2)
    
    # Настройка случайной геолокации
    lat = random.uniform(-90, 90)
    lon = random.uniform(-180, 180)
    profile.set_preference("geo.enabled", True)
    profile.set_preference("geo.provider.use_corelocation", True)
    profile.set_preference("geo.prompt.testing", True)
    profile.set_preference("geo.prompt.testing.allow", True)
    profile.set_preference("geo.wifi.uri", f"data:application/json,{{\"location\": {{\"lat\": {lat}, \"lng\": {lon}}}, \"accuracy\": 27000.0}}")

    options.profile = profile  # Устанавливаем профиль в опции

    if proxy:
        proxy_parts = proxy.split(':')
        if len(proxy_parts) == 4:  # Формат: login:pass@ip:port
            login, password = proxy_parts[0].split('@')
            ip, port = proxy_parts[1], proxy_parts[2]
            options.set_preference('network.proxy.type', 1)
            options.set_preference('network.proxy.http', ip)
            options.set_preference('network.proxy.http_port', int(port))
            options.set_preference('network.proxy.ssl', ip)
            options.set_preference('network.proxy.ssl_port', int(port))
            options.set_preference('network.proxy.socks', ip)
            options.set_preference('network.proxy.socks_port', int(port))
            options.set_preference('network.proxy.socks_username', login)
            options.set_preference('network.proxy.socks_password', password)
        elif len(proxy_parts) == 2:  # Формат: ip:port
            ip, port = proxy_parts
            options.set_preference('network.proxy.type', 1)
            options.set_preference('network.proxy.http', ip)
            options.set_preference('network.proxy.http_port', int(port))
            options.set_preference('network.proxy.ssl', ip)
            options.set_preference('network.proxy.ssl_port', int(port))

    current_dir = os.path.dirname(os.path.abspath(__file__))
    geckodriver_path = os.path.join(current_dir, "geckodriver.exe")
    service = Service(geckodriver_path)
    driver = webdriver.Firefox(service=service, options=options)
    
    logging.info(f"Создан драйвер с User-Agent: {user_agent}, GeoLocation: (lat: {lat}, lon: {lon})")  # Логируем используемый User-Agent и геолокацию

    return driver

def type_text_slowly(element, text, delay=0.1):
    """Функция для медленной печати текста в элемент."""
    for char in text:
        element.send_keys(char)
        time.sleep(delay)

def process_page(driver, url, message, stop_flag):
    try:
        logging.info(f"Попытка загрузки страницы: {url}")
        driver.set_page_load_timeout(30)
        driver.get(url)
        logging.info(f"Текущий URL после загрузки: {driver.current_url}")
        
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "Logo-Link")))
        logging.info("Элемент 'Logo-Link' найден")

        time.sleep(random.uniform(15, 20))  # Добавляем паузу в 15-20 секунд перед нажатием на кнопку "Чат"

        chat_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Чат']]"))
        )
        chat_button.click()
        logging.info("Кнопка 'Чат' нажата")
        time.sleep(random.uniform(13, 17))  # Добавляем паузу в 13-17 секунд перед нажатием на кнопку "Я.Мессенджер"

        try:
            messenger_button = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Я.Мессенджер')]"))
            )
            messenger_button.click()
            logging.info("Кнопка 'Я.Мессенджер' нажата")
            time.sleep(random.uniform(13, 17))  # Добавляем паузу в 13-17 секунд после нажатия на кнопку "Я.Мессенджер"
        except TimeoutException:
            logging.warning(f"Элемент 'Я.Мессенджер' не найден на странице {url}. Пробуем альтернативный XPath.")
            try:
                messenger_button_alt = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Я.Мессенджер')]"))
                )
                messenger_button_alt.click()
                logging.info("Альтернативная кнопка 'Я.Мессенджер' нажата")
                time.sleep(random.uniform(13, 17))  # Добавляем паузу в 13-17 секунд после нажатия на альтернативную кнопку "Я.Мессенджер"
            except TimeoutException:
                logging.warning(f"Элемент 'Я.Мессенджер' не найден на странице {url} даже с альтернативным XPath. Пропускаем это действие.")

        # Проверка наличия iframe и переключение на него
        try:
            iframe = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
            driver.switch_to.frame(iframe)
            logging.info("Переключились на iframe")
        except TimeoutException:
            logging.info("iframe не найден, продолжаем без переключения")

        # Берем строку из файла Текст.xlsx и пишем текст строки
        try:
            textarea = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[data-autofocus-container]"))
            )
            logging.info(f"Текстовое поле найдено на {url}")
            type_text_slowly(textarea, message)  # Используем функцию медленной печати
            logging.info(f"Текст введен в поле на {url}")
            time.sleep(random.uniform(4, 7))  # Подождем перед отправкой
        except (TimeoutException, NoSuchElementException) as e:
            logging.warning(f"Элемент текстового поля не найден на странице {url}. Пробуем альтернативный селектор. Ошибка: {str(e)}")
            try:
                textarea_alt = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.ui-textarea__control"))
                )
                logging.info(f"Альтернативное текстовое поле найдено на {url}")
                type_text_slowly(textarea_alt, message)  # Используем функцию медленной печати
                logging.info(f"Текст введен в альтернативное поле на {url}")
                time.sleep(random.uniform(4, 7))
            except (TimeoutException, NoSuchElementException) as e:
                logging.warning(f"Альтернативное текстовое поле не найдено на странице {url}. Пропускаем это действие. Ошибка: {str(e)}")
                return

        # Кликаем на кнопку отправить
        try:
            send_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.ui-icon-button_design_submit"))
            )
            send_button.click()
            logging.info(f"Кнопка отправки сообщения нажата на {url}")
            time.sleep(random.uniform(4, 7))  # Подождем после отправки
            logging.info(f"Сообщение отправлено на {url}")
        except (TimeoutException, NoSuchElementException) as e:
            logging.warning(f"Кнопка отправки сообщения не найдена на странице {url}. Пропускаем это действие. Ошибка: {str(e)}")
            return

        # Кликаем на кнопку "Не сейчас"
        try:
            not_now_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Не сейчас')]"))
            )
            not_now_button.click()
            logging.info(f"Кнопка 'Не сейчас' нажата на {url}")
            time.sleep(random.uniform(4, 7))  # Пауза после нажатия на "Не сейчас"
        except (TimeoutException, NoSuchElementException) as e:
            logging.warning(f"Кнопка 'Не сейчас' не найдена на странице {url}. Пропускаем это действие. Ошибка: {str(e)}")

        # Повторный клик на кнопку отправки сообщения
        try:
            send_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.ui-icon-button_design_submit"))
            )
            send_button.click()
            logging.info(f"Повторный клик на кнопку отправки сообщения на {url}")
        except (TimeoutException, NoSuchElementException) as e:
            logging.warning(f"Повторный клик на кнопку отправки сообщения не удался на странице {url}. Пропускаем это действие. Ошибка: {str(e)}")

    except TimeoutException:
        logging.error(f"Таймаут при загрузке страницы {url}")
    except WebDriverException as e:
        logging.error(f"Ошибка WebDriver при загрузке {url}: {str(e)}")
    except Exception as e:
        logging.error(f"Неизвестная ошибка при обработке {url}: {str(e)}", exc_info=True)

def start_process(url_file, message_file, proxy_file, threads, stop_flag):
    urls = load_file_content(url_file)
    messages = load_xlsx_content(message_file)
    proxies = load_file_content(proxy_file)

    logging.info(f"Запуск процесса с {threads} потоками")
    logging.info(f"Загружено {len(urls)} URL, {len(messages)} сообщений и {len(proxies)} прокси")

    while not stop_flag.is_set():
        if not urls:
            logging.info("Список URL пуст. Ожидаем добавления новых URL.")
            time.sleep(60)  # Пауза в 1 минуту
            urls = load_file_content(url_file)
            continue

        for _ in range(threads):
            if not urls:
                break

            url = urls.pop(0)  # Берем URL из начала списка
            save_file_content(url_file, urls)  # Сохранить обновленный список URL в файл

            proxy = random.choice(proxies) if proxies else None
            driver = create_driver(proxy)  # Создаем новый драйвер для каждого URL
            user_agent = driver.execute_script("return navigator.userAgent;")
            logging.info(f"Используем прокси: {proxy}, User-Agent: {user_agent}")  # Логирование уникальных параметров профиля

            message = get_random_line(messages)
            process_page(driver, url, message, stop_flag)

            driver.quit()  # Закрываем драйвер после обработки страницы

    logging.info("Процесс завершен")