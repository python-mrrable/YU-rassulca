import time
import random
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import logging
import os
from utils import load_file_content, load_xlsx_content, get_random_line

# Настройка логирования
logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='a')

def create_driver(proxy):
    options = Options()
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference('useAutomationExtension', False)
    options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0")
    
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
    return driver

def process_page(driver, url, message, stop_flag):
    try:
        logging.info(f"Попытка загрузки страницы: {url}")
        driver.set_page_load_timeout(30)
        driver.get(url)
        logging.info(f"Текущий URL после загрузки: {driver.current_url}")
        
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "Logo-Link")))
        
        chat_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Чат']]"))
        )
        chat_button.click()
        time.sleep(20)

        messenger_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Я.Мессенджер')]"))
        )
        messenger_button.click()
        time.sleep(20)

        textarea = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//textarea[@data-autofocus-container]"))
        )
        textarea.send_keys(message)
        time.sleep(random.uniform(4, 7))

        send_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'ui-icon-button_design_submit')]"))
        )
        send_button.click()
        time.sleep(random.uniform(15, 20))

        logging.info(f"Сообщение отправлено на {url}")

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

    for _ in range(threads):
        driver = create_driver(random.choice(proxies) if proxies else None)
        while not stop_flag.is_set():
            url = get_random_line(urls)
            message = get_random_line(messages)
            process_page(driver, url, message, stop_flag)
        driver.quit()

    logging.info("Процесс завершен")