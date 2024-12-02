import json
import time

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import tkinter as tk
from tkinter import messagebox


class AvitoParser:
    def __init__(self, key_words: list[str], page_count=1, max_price=20000) -> None:
        self.__url = "https://www.avito.ru/"
        self.__page_count = page_count
        self.__key_words = key_words
        self.max_price = max_price
        self.data = []

    def __set_up(self):
        """Инициализируем и настраиваем webdriver"""
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless")
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(options=self.options)
        # С помощью следующего пункта можно регулировать длительность ожидания загрузки страницы
        self.driver.set_page_load_timeout(5)

    def __get_url(self):
        try:
            self.driver.get(self.__url)
        except TimeoutException:
            pass

    def __search(self):
        """Осуществляем поиск по ключевым словам"""
        search_box = self.driver.find_element(By.XPATH, '//input[@data-marker="search-form/suggest/input"]')
        search_box.clear()
        for key_word in self.__key_words:
            search_box.send_keys(key_word)
            time.sleep(0.1)
            search_box.send_keys(Keys.SPACE)
        try:
            search_box.send_keys(Keys.ENTER)
        except TimeoutException:
            pass

    def __paginator(self):
        """Осуществляет перемещение по страницам и запускает парсинг"""
        while (self.driver.find_elements(By.XPATH, '//a[@data-marker="pagination-button/nextPage"]')
               and self.__page_count > 0):
            self.__parse_page()
            if self.__page_count > 1:
                try:
                    self.driver.find_element(By.XPATH, '//a[@data-marker="pagination-button/nextPage"]').click()
                except TimeoutException:
                    pass
            self.__page_count -= 1

    def __parse_page(self):
        """Парсинг страницы"""
        products = self.driver.find_elements(By.XPATH, '//div[@data-marker="item"]')
        for product in products:
            title = product.find_element(By.XPATH, './/h3[@itemprop="name"]').text
            price = product.find_element(By.XPATH, './/meta[@itemprop="price"]').get_attribute('content')
            description = product.find_element(By.XPATH, ".//div[contains(@class, 'iva-item-description')]/p").text
            url = product.find_element(By.XPATH, './/a[@itemprop="url"]').get_attribute('href')
            data = {
                'title': title,
                'price': price,
                'description': description,
                'url': url,
            }
            if int(price) <= self.max_price:
                self.data.append(data)
        self.__save_data()

    def __save_data(self):
        """Сохраняем отобранную информацию"""
        with open('items.json', 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

    def parse(self):
        self.__set_up()
        self.__get_url()
        self.__search()
        self.__paginator()


def start_parser():
    """Собирает информацию, поступившую от пользователя через графический интерфейс и запускает на ее основе парсер"""
    key_words = [key_word.strip() for key_word in key_words_entry.get().split(',')]
    page_count = int(pages_entry.get())
    max_price = int(max_price_entry.get())
    parser = AvitoParser(key_words=key_words, page_count=page_count, max_price=max_price)
    parser.parse()
    messagebox.showinfo("Информация", "Парсинг завершен. Результаты сохранены в items.json.")


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Avito Parser")

    tk.Label(root, text="Введите элементы для поиска (через запятую):").grid(row=0, column=0, padx=10, pady=10)
    key_words_entry = tk.Entry(root, width=50)
    key_words_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="Введите количество страниц:").grid(row=1, column=0, padx=10, pady=10)
    pages_entry = tk.Entry(root, width=10)
    pages_entry.grid(row=1, column=1, padx=10, pady=10)
    pages_entry.insert(0, '1')

    tk.Label(root, text="Введите максимально допустимую стоимость:").grid(row=2, column=0, padx=10, pady=10)
    max_price_entry = tk.Entry(root, width=10)
    max_price_entry.grid(row=2, column=1, padx=10, pady=10)
    max_price_entry.insert(0, '20000')

    tk.Button(root, text="Запуск парсера", command=start_parser).grid(row=3, column=0, columnspan=2, padx=10, pady=20)

    root.mainloop()
