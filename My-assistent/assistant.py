import keyboard
import logging
import vosk
import sys
import re
import webbrowser
import requests
import queue
import time
import json

import cv2
import mediapipe as mp
import matplotlib.pyplot as plt
import speech_recognition as sr
import sounddevice as sd
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from num2words import num2words

import pyautogui 
import wmi 


logger = logging.getLogger(__name__)



WEATHER_API_KEY = '78de1db61ffa6efd32239911ca57f068'
weather_url = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={api_key}&lang=ua"



api_key = '78de1db61ffa6efd32239911ca57f068'

def get_weather(city, date):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'
    response = requests.get(url)
    data = response.json()
    if 'weather' in data:
        weather_description = data['weather'][0]['description']
        # Переведення температури з Кельвіна у Цельсій
        temperature_kelvin = data['main']['temp']
        temperature_celsius = round(temperature_kelvin - 273.15, 2)
        # Перевірка для округлення температури
        if temperature_celsius % 1 >= 0.5:
            temperature_celsius = int(temperature_celsius) + 1
        else:
            temperature_celsius = int(temperature_celsius)
        # Перевірка дати
        if date == "сьогодні":
            date = datetime.now().date()
        elif date == "завтра":
            date = datetime.now().date() + timedelta(days=1)
        elif date == "післязавтра":
            date = datetime.now().date() + timedelta(days=2)
        # Використання num2words для перетворення чисел у слова
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        # Переклад опису погоди
        translation = translations.get(weather_description, weather_description)
        return f'Погода в місті {city} на сьогодні: {translation}. Температура: {num2words(temperature_celsius, lang="uk")} градусів Цельсія. Вологість: {num2words(humidity, lang="uk")} відсотків.'# Швидкість вітру: {num2words(wind_speed, lang="uk")} метрів в секунду.'
    else:
        return f'Дані про погоду для міста {city} на {date} не знайдені.'

translations = {
    "clear sky": "ясне небо",
    "few clouds": "невелика хмарність",
    "scattered clouds": "хмарно з проясненнями",
    "broken clouds": "хмарно з проясненнями",
    "overcast clouds": "похмуро",
    "light rain": "невеликий дощ",
    "moderate rain": "помірний дощ",
    "heavy intensity rain": "сильний дощ",
}

def process_city_name(city):
    # Видаляємо "і" в кінці назви міста, якщо вона є
    if city.endswith('і'):
        city = city[:-1]
    return city

def get_date():
    return datetime.now().date()

def set_monitor_brightness(brightness_level):
    # Відображення чисел словами на числове значення
    numbers = {'один': 1, 'два': 2, 'три': 3, 'чотири': 4, 'п\'ять': 5, 'шість': 6, 'сім': 7, 'вісім': 8, 'дев\'ять': 9, 'десять': 10,
               'одинадцять': 11, 'дванадцять': 12, 'тринадцять': 13, 'чотирнадцять': 14, 'п\'ятнадцять': 15, 'шістнадцять': 16, 
               'сімнадцять': 17, 'вісімнадцять': 18, 'дев\'ятнадцять': 19, 'двадцять': 20, 'тридцять': 30, 'сорок': 40, 'п\'ятдесят': 50,
               'шістдесят': 60, 'сімдесят': 70, 'вісімдесят': 80, 'дев\'яносто': 90}
    
    # Розбиваємо рядок запиту на окремі слова
    words = brightness_level.split()
    
    # Ініціалізуємо змінну для зберігання загального числового значення
    total_brightness = 0
    
    # Проходимося по кожному слову і додаємо його числове значення до загального числового значення
    for word in words:
        if word.lower() in numbers:
            total_brightness += numbers[word.lower()]
    
    # Встановлення яскравості
    c = wmi.WMI(namespace='wmi')
    methods = c.WmiMonitorBrightnessMethods()[0]
    methods.WmiSetBrightness(total_brightness, 0)
    print(f"Яскравість була змінена на {total_brightness}.")

def play_video(question):
    webbrowser.open("https://www.youtube.com")

    time.sleep(5)

    pyautogui.click(600, 200)

    search_term = re.search(' відео (.+)', question)
    if search_term:
        search_term = search_term.group(1).replace(' ', '_')

        keyboard.write(search_term)
        time.sleep(1)
        keyboard.press("enter")

        time.sleep(2)

        pyautogui.click(350, 400)

        time.sleep(5)

    else:
        # Если запрос пустой, выводим сообщение об ошибке
        print("Запит не розпізнано")