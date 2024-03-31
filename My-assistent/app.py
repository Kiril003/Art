import logging
import sys
import threading
import json
import re
import time
import requests
import wmi
import random
import pyaudio
import os
import pyautogui
import webbrowser
import wikipedia
import keyboard
import datetime
import geocoder
import webbrowser
import torch
import cv2
import feedparser, queue
from num2words import num2words
from deep_translator import GoogleTranslator
import pythoncom, vosk
from vosk import Model, KaldiRecognizer
import pyperclip
import subprocess, soundfile, tempfile

import ctypes
import win32com.client as wincl
import pygetwindow as gw
import sounddevice as sd
import speech_recognition as sr
import tkinter as tk
import datetime as dt
from fuzzywuzzy import fuzz
from PIL import Image, ImageTk, ImageGrab
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import pygame
from ru_word2number import w2n
from scheduler import Scheduler, SchedulerError
from playsound import playsound
from bs4 import BeautifulSoup
from pynput.keyboard import Controller
from pynput.keyboard import Key, Controller as KeyboardController
from tkinter import Tk, Label, Entry, Button, Text, Frame, Scrollbar
from tkinter import messagebox as mb
import matplotlib.pyplot as plt
from word2number import w2n
import tkinter as tk

from assistant import get_weather, get_date, process_city_name, set_monitor_brightness #execute_command

from log_init import init_logger
from main_window import Ui_MainWindow
from reminder import get_reminder_settings
from threading import Thread

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume



init_logger()
logger = logging.getLogger('app.main')

REMINDER_SOUND_PATH = "C:\\My-assistent\\beep.mp3"
DAYS_OF_WEEK = {1: 'Пн', 2: 'Вт', 3: 'Ср', 4: 'Чт', 5: 'Пт', 6: 'Сб', 7: 'Нд'}
MAX_TASKS = 20

weather_recommendations = {
    "clear sky": [
        "Одягніться легко і візьміть сонцезахисні окуляри. Можете вирушити на пікнік або прогулянку в парк.",
        "Завітайте на пляж і насолоджуйтесь сонячним днем.",
        "Виберіть активне дозвілля на свіжому повітрі, наприклад, велосипедний прогін."
    ],
    "few clouds": [
        "Одягніться комфортно. Гарно підходить для прогулянок.",
        "Вирушіть на прогулянку і насолоджуйтесь красивим видом на хмари.",
        "Проведіть час на відкритому повітрі, наприклад, грати у волейбол або футбол."
    ],
    "scattered clouds": [
        "Одягніться тепліше. Можете вирушити на прогулянку.",
        "Вирушіть на природу і насолоджуйтесь переглядом різних хмарних форм.",
        "Виберіть прогулянку по парку або в гори, щоб побачити розкидані хмари."
    ],
    "overcast clouds": [
        "Одягніться тепліше і візьміть парасольку на випадок дощу.",
        "Плануйте відпочинок у приміщенні, наприклад, відвідати музей або кінотеатр.",
        "Рекомендується відвідати кав'ярню або книгарню та провести час у затишній атмосфері."
    ],
    "light rain": [
        "Одягніться тепліше і візьміть парасольку. Рекомендується залишатися вдома.",
        "Проведіть час вдома, читаючи книгу або дивлячись фільм.",
        "Заплануйте готування смачних страв або печіння, щоб зробити затишний день вдома."
    ],
    "moderate rain": [
        "Одягніться тепліше і візьміть парасольку. Рекомендується залишатися вдома.",
        "Займіться творчістю вдома, малюючи або граючи на музичних інструментах.",
        "Організуйте день вдома з сім'єю або друзями, граючи в настільні ігри або дивлячись фільми."
    ],
    "heavy intensity rain": [
        "Одягніться тепліше і візьміть парасольку. Краще залишитися вдома.",
        "Заплануйте теплий день вдома, з чашкою гарячого чаю або какао.",
        "Віддайте перевагу домашнім заняттям, таким як розробка проектів або ремесла."
    ]
}

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

letter_mapping = {
    'a': 'а',
    'b': 'б',
    'c': 'ц',
    'd': 'д',
    'e': 'е',
    'f': 'ф',
    'g': 'ґ',
    'h': 'г',
    'i': 'і',
    'j': 'й',
    'k': 'к',
    'l': 'л',
    'm': 'м',
    'n': 'н',
    'o': 'о',
    'p': 'п',
    'q': 'к',
    'r': 'р',
    's': 'с',
    't': 'т',
    'u': 'у',
    'v': 'в',
    'w': 'в',
    'x': 'х',
    'y': 'и',
    'z': 'з'
}

num_words_to_digits = {
    "один": 1,
    "два": 2,
    "три": 3,
    "чотири": 4,
    "п'ять": 5,
    "шість": 6,
    "сім": 7,
    "вісім": 8,
    "дев'ять": 9,
    "десять": 10,
    "одинадцять": 11,
    "дванадцять": 12,
    "тринадцять": 13,
    "чотирнадцять": 14,
    "п'ятнадцять": 15,
    "шістнадцять": 16,
    "сімнадцять": 17,
    "вісімнадцять": 18,
    "дев'ятнадцять": 19,
    "двадцять": 20,
    "тридцять": 30,
    "сорок": 40,
    "п'ятдесят": 50,
    "шістдесят": 60,
    "сімдесят": 70,
    "вісімдесят": 80,
    "дев'яносто": 90,
    "сто": 100,
}

recognize_model = vosk.Model("C:\\My-assistent\\vosk-model-uk-v3")
recognition_samplerate = 16000
device = 1

q = queue.Queue()
def q_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def recognize_speech(index=0):
    with sd.RawInputStream(
            samplerate=recognition_samplerate,
            blocksize=1000,
            device=device,
            dtype='int16',
            channels=1,
            callback=q_callback
    ):
        rec = vosk.KaldiRecognizer(recognize_model, recognition_samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                voice_input = json.loads(rec.Result())["text"]
                return voice_input
    return ""

def open_email():
    email_url = "https://mail.google.com" 
    webbrowser.open(email_url)

def play_audio(file_path):
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    # Чекаємо, доки аудіофайл не закінчиться
    while pygame.mixer.music.get_busy():
        continue

    pygame.mixer.quit()
    pygame.quit()

class AppUI(Ui_MainWindow):

    def __init__(self):
        self.main_window: QtWidgets.QMainWindow = None
        self.scheduler = Scheduler()
        self.country = None
        self.city = None
        self.weather = dict()
        self.weather_pic = None
        self.voices = {"mykyta": "mykyta", "mykyta": "mykyta", "mykyta": "mykyta"}
        self.voice = None
        self.settings_file = "C:\\My-assistent\\settings.json"
        self.speaker, self.music_path, self.background = self.get_user_settings()
        self.run = False
        self.tasks = dict()
        self.tasks_to_remove = list()
        self.task_frames = dict()
        self.dialog_process = None
        self.update_process = None
        self.dialog_process_stop = False
        self.update_process_stop = False
        self.time_format = "%H:%M:%S"
        self.date_format = "%d.%m.%y"
        self.check_button_icon = QtGui.QIcon()
        self.check_button_icon.addPixmap(QtGui.QPixmap("C:/My-assistent/icons/check-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self._translate = QtCore.QCoreApplication.translate
        self.start_assistant_process()
        self.tts_model = None
        self.tts_model_path = "C:\\My-assistent\\v3_ua.pt"
        self.load_tts_model()

    def load_tts_model(self):
        if self.tts_model_path and os.path.isfile(self.tts_model_path):
            torch.set_num_threads(4)
            self.tts_model = torch.package.PackageImporter(self.tts_model_path).load_pickle("tts_models", "model")
            self.tts_model.to(torch.device('cpu'))
        else:
            print("Шлях до моделі TTS не знайдено або не вказано")

    def play_tts(self, text):
        if self.tts_model:
            sample_rate = 48000
            speaker = 'mykyta'
            audio = self.tts_model.apply_tts(text=text,
                                            speaker=speaker,
                                            sample_rate=sample_rate,
                                            put_accent=True,
                                            put_yo=True)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                filename = f.name
                soundfile.write(filename, audio, sample_rate, format='WAV')

            # Створення QMediaPlayer
            self.player = QMediaPlayer()  # Зробіть його атрибутом класу
            self.media_content = QMediaContent(QtCore.QUrl.fromLocalFile(filename))
            self.player.setMedia(self.media_content)

            # Зв'язка сигналу відтворення завершення з методом для видалення файлу
            self.player.stateChanged.connect(lambda state: self.handle_player_state_changed(state, filename))

            # Відтворення аудіо
            self.player.play()

    def handle_player_state_changed(self, new_state, filename):
        if new_state == QMediaPlayer.StoppedState:
            os.remove(filename)  # Видалення тимчасового файлу після завершення відтворення

    def load_user_settings(self):
        with open(self.settings_file, 'r') as f:
            json_data = f.read()
        settings = json.loads(json_data)
        return settings

    def get_user_settings(self):
        settings = self.load_user_settings()
        return settings['speaker'], settings['music_path'], settings['background']

    def update_user_settings(self, **kwargs):
        settings = self.load_user_settings()
        settings.update(**kwargs)
        with open(self.settings_file, 'w') as f:
            f.write(json.dumps(settings))

    def get_file_path(self, folder: str):
        file_dialog = QtWidgets.QFileDialog(self.options_widget)
        file_dialog.setNameFilters(["Изображения (*.png *.jpg *.jpeg *.gif)"])
        file_dialog.default_filter_index = 0
        file_dialog.setDirectory(folder)
        file_dialog.exec()
        # file_path = file_dialog.getOpenFileName(
        #     self.options_widget, caption='Выберите файл фона', directory=folder
        # )
        return file_dialog.selectedFiles()[0]

    def task_button_action(self, task_id: int):
        frame: QtWidgets.QFrame = self.task_frames[task_id]
        button: QtWidgets.QPushButton = frame.findChildren(QtWidgets.QPushButton)[0]
        if task_id in self.tasks_to_remove:
            self.tasks_to_remove.remove(task_id)
            button.setIcon(self.check_button_icon)
        else:
            self.tasks_to_remove.append(task_id)
            button.setIcon(QtGui.QIcon())

    def build_task_frame(self, task_id: int):
        task_frame = QtWidgets.QFrame(self.task_scrollarea_content)
        task_frame.setGeometry(QtCore.QRect(0, 10 + 50 * task_id, 430, 40))
        task_frame.setStyleSheet("border: none;")
        task_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        task_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        task_frame.setObjectName(f"task{task_id}_frame")
        task_widget = QtWidgets.QWidget(task_frame)
        task_widget.setGeometry(QtCore.QRect(40, 0, 390, 35))
        task_widget.setStyleSheet("border-bottom: 2px solid #c8c863;")
        task_widget.setObjectName(f"task{task_id}_widget")
        task_name_label = QtWidgets.QLabel(task_widget)
        task_name_label.setGeometry(QtCore.QRect(40, 8, 200, 25))
        task_name_label.setStyleSheet("border: none;")
        task_name_label.setObjectName(f"task{task_id}_name_label")
        task_datetime_label = QtWidgets.QLabel(task_widget)
        task_datetime_label.setGeometry(QtCore.QRect(210, 5, 181, 28))
        task_datetime_label.setStyleSheet("border: none;\nfont: 75 10pt \"Myriad Pro Cond\";\ncolor: rgb(0, 230, 0);")
        task_datetime_label.setObjectName(f"task{task_id}_datetime_label")
        task_check_button = QtWidgets.QPushButton(task_widget)
        task_check_button.setGeometry(QtCore.QRect(3, 5, 30, 30))
        task_check_button.setStyleSheet("border: 2px solid #c8c863;")
        task_check_button.setText("")
        task_check_button.setIcon(QtGui.QIcon())
        task_check_button.setIconSize(QtCore.QSize(25, 25))
        task_check_button.setFlat(True)
        task_check_button.setObjectName(f"task{task_id}_check_button")
        self.task_frames.update({task_id: task_frame})

    def create_task_frames(self):
        logger.info('Creating task frames')
        scrollarea_height = MAX_TASKS * 50 + 15
        self.task_scrollarea_content.setMinimumHeight(scrollarea_height)
        for i in range(MAX_TASKS):
            self.build_task_frame(i)

    def rebuild_tasks(self):
        logger.info('Rebuilding task frames')
        self.tasks_frame.close()
        if self.tasks_to_remove:
            n = 1
            for task_id in self.tasks_to_remove:
                self.set_task_frame_ui(task_id, '', None, create=False)
                task_frame = self.task_frames.pop(task_id)
                self.task_frames[MAX_TASKS + n] = task_frame
                n += 1
            self.tasks = {i: t for i, t in enumerate(self.tasks.values())}
            self.task_frames = {i: frame for i, frame in enumerate(self.task_frames.values())}
            for i, frame in self.task_frames.items():
                frame.setGeometry(QtCore.QRect(0, 10 + 50 * i, 430, 40))
                task_check_button: QtWidgets.QPushButton = frame.findChildren(QtWidgets.QPushButton)[0]
                task_check_button.clicked.connect(lambda: self.task_button_action(task_id=i))
            self.tasks_to_remove = list()

    def remind_task(self, task_id: int, task_text: str):
        play_audio(REMINDER_SOUND_PATH)
        self.play_tts('Нагадую ' + task_text)
        self.tasks_to_remove = [task_id]
        self.rebuild_tasks()

    def get_task_datetime_text(self, task_dt: dt.datetime):
        task_time = task_dt.strftime('%H:%M')
        task_date = task_dt.strftime('%d.%m.%Y')
        task_day_of_week = DAYS_OF_WEEK[task_dt.isoweekday()]
        return f'{task_time} {task_day_of_week} {task_date}'

    def schedule_task(self, task_id: int, task_dt: dt.datetime, task_text: str):
        logger.info(f'Schedule task {task_id} {task_text} {task_dt}')
        task = self.scheduler.once(
            task_dt,
            self.remind_task,
            args=(task_id, task_text)
        )
        self.tasks[task_id] = task
        print()

    def set_task_frame_ui(self, task_id: int, task_text: str, task_dt: dt.datetime, create: bool):
        logger.info(f'Setting task {task_id} frame UI: {task_text} {task_dt}')
        if task_dt:
            task_dt = self.get_task_datetime_text(task_dt)
        else:
            task_dt = ''
        new_task_frame = self.task_frames[task_id]
        labels = new_task_frame.findChildren(QtWidgets.QLabel)
        new_task_name_label = labels[0]
        new_task_datetime_label = labels[1]
        task_check_button: QtWidgets.QPushButton = new_task_frame.findChildren(QtWidgets.QPushButton)[0]
        if create:
            task_check_button.setIcon(self.check_button_icon)
            task_check_button.clicked.connect(lambda: self.task_button_action(task_id=task_id))
        else:
            task_check_button.setIcon(QtGui.QIcon())
            task_check_button.disconnect()
        new_task_name_label.setText(self._translate(
            "MainWindow",
            f"<html><head/><body><p><span style=\" font-size:10pt;\">{task_text}</span></p></body></html>"
        ))
        new_task_datetime_label.setText(self._translate(
            "MainWindow",
            "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600;\">"
            f"{task_dt}</span></p></body></html>"
        ))
        logger.info(f'Task frame {task_id} set')

    def create_task(self, task_text: str, task_dt: dt.datetime):
        logger.info(f'Creating task {task_text} {task_dt}')
        new_task_id = 0
        tasks_ids = sorted(list(self.tasks.keys()))
        if tasks_ids:
            new_task_id = tasks_ids[-1] + 1
        self.schedule_task(new_task_id, task_dt, task_text)
        self.set_task_frame_ui(new_task_id, task_text, task_dt, create=True)
        print()

    def update_ui(self):
        self.app_background.setPixmap(QtGui.QPixmap(self.background))
        self.options_widget.setHidden(True)
        self.tasks_frame.setHidden(True)
        self.voices_widget.setHidden(True)
        self.date_label.setMargin(10)
        self.time_label.setMargin(10)
        self.create_task_frames()

    def set_buttons_commands(self):
        self.option_button.clicked['bool'].connect(self.options_widget.setVisible)
        self.background_option_button.clicked.connect(self.set_background_file)
        self.telegram_option_button.clicked.connect(self.open_telegram)
        self.music_option_button.clicked.connect(self.set_music_path)
        self.clear_dialog_button.clicked.connect(self.clear_all)
        # self.clear_dialog_button.clicked.connect(self.test_func)
        self.voice_option_button.clicked.connect(self.voices_widget.show)
        self.voice_ok_button.clicked.connect(self.voices_widget.close)
        self.baya_voice_button.clicked.connect(lambda: self.voice_button_action(self.baya_voice_button))
        self.xenia_voice_button.clicked.connect(lambda: self.voice_button_action(self.xenia_voice_button))
        self.kseniya_voice_button.clicked.connect(lambda: self.voice_button_action(self.kseniya_voice_button))
        self.dialog_button.clicked.connect(self.start_dialog)
        self.date_button.clicked.connect(self.tasks_frame.show)
        self.save_tasks_button.clicked.connect(self.rebuild_tasks)
        self.search_button.clicked.connect(self.text_search_in_wiki)
        # self.search_button.clicked.connect(self.test_func)

    def setupUi(self, window: QtWidgets.QMainWindow):
        super().setupUi(window)
        self.main_window = window
        self.update_ui()
        self.set_buttons_commands()
        # self.create_task('помыть посуду', dt.datetime(year=2023, month=5, day=5, hour=5, minute=42))
        # self.create_task('вынести мусор', dt.datetime(year=2023, month=5, day=5, hour=6, minute=42))
        # self.create_task('покрасить стены', dt.datetime(year=2023, month=5, day=5, hour=7, minute=42))
        # self.create_task('переклеить обои', dt.datetime(year=2023, month=5, day=5, hour=8, minute=42))
        self.run_info_update_tread()

    def search(self, text):
        google_search = f"https://www.google.com.ua/search?q={text.replace(' ', '+')}"
        webbrowser.open(google_search)

    def set_background_file(self):
        file_dialog = QtWidgets.QFileDialog(self.options_widget)
        file_dialog.setNameFilters(["Изображения (*.png *.jpg *.jpeg *.gif)"])
        file_dialog.default_filter_index = 0
        file_dialog.setDirectory(os.path.expanduser(r'~\Pictures'))
        file_dialog.exec()
        # file_path = file_dialog.getOpenFileName(
        #     self.options_widget, caption='Выберите файл фона', directory=folder
        # )
        background_path = file_dialog.selectedFiles()[0]
        self.app_background.setPixmap(QtGui.QPixmap(background_path))
        self.update_user_settings(background=background_path)

    def set_music_path(self):
        file_dialog = QtWidgets.QFileDialog(self.options_widget)
        file_dialog.setDirectory(os.path.expanduser(r'~\Music'))
        self.music_path = file_dialog.getExistingDirectory()
        self.update_user_settings(music_path=self.music_path)

    def clear_all(self):
        self.dialog_text_label.setText(self._translate(
            "MainWindow",
            "<html><head/><body><p><span style=\" font-size:6pt; font-weight:550; color:#ffcccc;\">Ви: ..."
            "</span></p><p><span style=\" font-size:7pt; font-weight:600; color:#ffaa00;\">Art: ..."
            "</span></p></body></html>"))
        self.search_result_label.setText(self._translate(
            "MainWindow",
            "<html><head/><body><p><span style=\" font-size:6pt; font-weight:600; color:#00d5ff;\">Результаты поиска</span></p></body></html>"
        ))

    def test_func(self):
        text = self.search_line_input.text()
        self.set_voice_reminder(text, command='нагадай мені')
        # self.create_task('помыть посуду', dt.datetime(year=2023, month=5, day=15, hour=3, minute=40))
        # self.create_task('вынести мусор', dt.datetime(year=2023, month=5, day=15, hour=4, minute=42))
        # self.create_task('покрасить стены', dt.datetime(year=2023, month=5, day=15, hour=5, minute=42))
        # self.create_task('переклеить обои', dt.datetime(year=2023, month=5, day=15, hour=6, minute=42))

    def voice_button_action(self, button):
        voice_buttons = [self.kseniya_voice_button, self.baya_voice_button, self.xenia_voice_button]
        button.setStyleSheet("border: none;\nfont: 75 13pt \"MS Shell Dlg 2\";\n"
                             "background-color: rgb(0, 200, 200);\nborder-radius: 12px;")
        self.speaker = self.voices[button.text()]
        for b in voice_buttons:
            if b != button:
                b.setStyleSheet("border: none;\nfont: 75 10pt \"MS Shell Dlg 2\";\n"
                                "background-color: rgb(85, 255, 255);\nborder-radius: 12px;")
        self.update_user_settings(speaker=self.speaker)

    def find_text_in_doc(self) -> str:
        text_to_find = ""
        try:
            text_to_find = self.search_line_input
            if self.word.ActiveDocument is not None and self.word.Selection is not None:
                self.word.Selection.Find.ClearFormatting()
                self.word.Selection.Find.Execute(text_to_find)
                if self.word.Selection.Find.Found:
                    answer = f"Текст {text_to_find} знайдено"
                else:
                    answer = f"Текст {text_to_find} не знайдений"
            else:
                
                answer = "Документ не відкритий. Будь ласка, відкрийте документ перед пошуком тексту."
        except Exception as e:
            answer = ("Не вдалося виконати пошук. Будь ласка, переконайтеся, що документ відкритий і ви правильно назвали шуканий текст.")
            logger.exception(e)
        return answer

    def question_contains(self, question: str, commands: list[str]) -> bool:
        for com in commands:
            if com in question:
                return True
            continue
        return False

    def answer_greetings(self) -> str:
        hour = datetime.datetime.now().hour
        if 4 <= hour < 12:
            answer = "Доброго ранку"
        elif 12 <= hour < 16:
            answer = "Доброго дня"
        elif 16 <= hour < 22:
            answer = "Доброго вечора"
        else:
            answer = "Доброї ночі"
        return answer

    def start_music(self):
        try:
            songs = os.listdir(self.music_path)
            song = random.choice(songs)
            os.startfile(os.path.join(self.music_path, song))
            answer = None
        except Exception as e:
            logger.exception(f'Не вдається увімкнути пісні\n{e}')
            answer = "Не вдається увімкнути пісні"
        return answer

    def enter_request(self, command: str, question: str):
        search_term = re.search(command + ' (.+)', question)
        if search_term:
            search_term = search_term.group(1).replace(' ', ' ')
            keyboard.write(search_term)

    def update_dialog(self, speaker: str, text: str):
        if speaker == 'you':
            new_text = ("<html><head/><body><p><span style=\" font-size:8pt; font-weight:600; color:#ff0000;\">Ви: "
                        f"{text}</span></p>")
        else:
            new_text = ("<html><head/><body><p><span style=\" font-size:8pt; font-weight:500; color:#ffaa00;\">"
                        f"Art: {text}</span></p></body></html>")
        current_text = self.dialog_text_label.text()
        # print('Text:', current_text)
        self.dialog_text_label.setText(current_text + new_text)

    def repeat_after_me(self, command: str, question: str):
        match = re.search(command + ' (.+)', question)
        if match:
            answer = match.group(1)
        else:
            answer = "Я не розумію, що мені повторювати"
        return answer

    def tell_current_time(self) -> str:
        current_time = datetime.datetime.now().strftime("%H:%M")
        words = []
        for num in current_time.split(":"):
            if num.startswith("0"):
                num = num[1:]
            words.append(num2words(int(num), lang='uk'))
        return "Зараз " + " ".join(words)

    def tell_current_day(self) -> str:
        MONTH_NAMES = {1: 'січня', 2: 'лютого', 3: 'березня', 4: 'квітня', 5: 'травня', 6: 'червня',
                        7: 'липня', 8: 'серпня', 9: 'вересня', 10: 'жовтня', 11: 'листопада', 12: 'грудня'}
        now = datetime.datetime.now()
        day = num2words(now.day, lang='uk')
        month = MONTH_NAMES[now.month]
        year = num2words(now.year, lang='uk')
        return f"Сьогодні {day} {month}"

    def voice_search_in_wiki(self, question: str):
        logger.info("Голосовий пошук у вікі")
        response = self.search_in_wiki(question)
        if not response:
            response = "Ви не вказали запит для пошуку"

        self.play_tts(response)

    def text_search_in_wiki(self):
        question: str = self.search_line_input.text()
        self.search_line_input.clear()
        if question.startswith(r'\\'):
            self.set_voice_reminder(question, r'\\')
            return
        original_response = self.search_in_wiki(question)
        if not original_response:
            original_response = "Ви не ввели запит"

        self.search_result_label.setText(self._translate(
            "MainWindow",
            "<html><head/><body><p><span style=\" font-size:8pt; font-weight:600; color:#00d5ff;\">"
            f"{original_response}</span></p></body></html>"
        ))

        def speak_translated_response():
            # Преобразование чисел в слова для озвучивания
            translated_response = original_response
            numbers = re.findall(r'\b\d+\b', translated_response)
            for number in numbers:
                word_number = num2words(int(number), lang='uk')
                translated_response = translated_response.replace(number, word_number)

            self.play_tts(translated_response)

        # Создание и запуск потока для озвучивания
        thread = threading.Thread(target=speak_translated_response)
        thread.start()

    def search_in_wiki(self, question: str):
        logger.info("Пошук у вікіпедії")
        if question and question != "":
            wikipedia.set_lang("uk")
            try:
                page = wikipedia.page(question)
                summary = page.content.split('\n')[0]
                summary = re.sub(r'\([^)]*\)', '', summary)  # исключаем текст в скобках
                return summary
            except wikipedia.exceptions.DisambiguationError as e:
                return f"Занадто багато можливих визначень для запиту \"{question}\". Спробуйте уточнити запит."
            except wikipedia.exceptions.PageError as e:
                return f"Не знайдено статей, що відповідають запиту \"{question}\"."
            except Exception as e:
                logger.exception(f"Сталася помилка: {e}")
                return f"Під час пошуку виникла помилка"
        else:
            return

            # search_term = question.group(1).replace(' ', '_')
            # wiki_url = f"https://ru.wikipedia.org/wiki/{search_term}"
            # webbrowser.open(wiki_url)

    def close_tabs(self, tabs_number: str):
        n = w2n.word_to_num(tabs_number)
        for i in range(n):
            keyboard.press_and_release('ctrl+w')
            time.sleep(1)

    def open_tabs(self, tabs_number: str):
        n = w2n.word_to_num(tabs_number)
        for i in range(n):
            keyboard.press_and_release('ctrl+t')
            time.sleep(1)

    def set_voice_reminder(self, text: str, command: str):
        text = text.replace(command, '').strip()
        logger.info(f'Setting a voice reminder by commend {command}:\n{text}')
        reminder_datetime, text, err = get_reminder_settings(text)
        logger.info(f'Got reminder settings {reminder_datetime}, {text}, {err}')
        if err:
            self.play_tts(err)
            return
        self.create_task(text, reminder_datetime)

    # def play_tts(self, text: str):
    #     speak(text, self.speaker)

    """ VOICE ASSISTANT """

    def run_assistant(self):
        while not self.dialog_process_stop:
            # print(self.run)
            if self.run:
                answer = None
                question = recognize_speech()
                if question == "":
                    #time.sleep(0.1)
                    continue
                self.update_dialog(speaker='you', text=question)
                
                if "зроби яскравіше" in question or "підвищи яскравість" in question or "збільши яскравість" in question or "підніми яскравість" in question:
                    pythoncom.CoInitialize()
                    brightness = wmi.WMI(namespace='wmi').WmiMonitorBrightness()[0].CurrentBrightness
                    new_brightness = int(min(brightness + 20, 100))
                    wmi.WMI(namespace='wmi').WmiMonitorBrightnessMethods()[0].WmiSetBrightness(new_brightness, 0)
                    answer = "Яскравість підвищена"
                if "зроби тьмяніше" in question or "знизь яскравість" in question or "зменьши яскравість" in question or "зменш яскравість" in question or "опусти яскравість" in question:
                    pythoncom.CoInitialize()
                    current_brightness = wmi.WMI(namespace='wmi').WmiMonitorBrightness()[0].CurrentBrightness
                    new_brightness = max(1, current_brightness - int(255 * 0.1))
                    wmi.WMI(namespace='wmi').WmiMonitorBrightnessMethods()[0].WmiSetBrightness(new_brightness, 0)
                    answer = "Яскравість знижена"
                
                if "відкрий фільм" in question or "увімкни фільм" in question:
                    k_url = "https://kinokong.pro/filmes/"
                    webbrowser.open(k_url)

                if "відкрий пошту" in question or "відкрий електронну пошту" in question or "відкрити пошту" in question:
                    open_email()

                # if "натисни на" in question:
                #     target_text = question.split("натисни на", 1)[-1].strip()
                #     print(target_text)
                #     # Створення та запуск окремого потоку для виконання команди
                #     command_thread = threading.Thread(target=execute_command, args=(target_text,))
                #     command_thread.start()
                if "як справи" in question:
                    random_answers = [
                                        "Неймовірно добре! Як у вас?",
                                        "Прекрасно, дякую! А ви як?",
                                        "Відмінно! Як ваші справи?",
                                        "З прекрасним настроєм! А ви як?",
                                        "Фантастично! А як у вас?",
                                        "Дуже добре, спасибі! Як ви себе почуваєте?",
                                        "Чудово, а ви як справи?",
                                        "Все чудово, дякую за запитання! А у вас?",
                                        "Суперово! А ви як почуваєте себе?",
                                        "Здорово! Як ваш день?",
                                        "Прекрасно! Як проходить ваш день?",
                                        "Чудовий настрій! А ви як?",
                                        "Добре, дякую! А у вас як?",
                                        "Шикарно! Як ваш настрій?",
                                        "Відмінно! Як ви відчуваєте себе?",
                                        "Запитуйте що завгодно, я завжди на зв'язку! А як у вас?",
                                        "Відмінно собі! А у вас як?",
                                        "Прекрасно, спасибі за турботу! Як ви?",
                                        "Чудово проводжу час! Як у вас справи?",
                                        "Відмінно, як у вас?",
                                        "Чудово почуваюся! А ви як?",
                                        "Дуже гарно! Як ваш настрій?",
                                        "Відмінно відпочиваю! Як ви?",
                                        "Чудовий день! Як у вас?",
                                        "Добре, дякую за запитання! А у вас як настрій?",
                                        "Феноменально! Як ви себе почуваєте?",
                                        "Прекрасно проводжу час! А ви як справи?",
                                        "Захоплююче! Як ви відчуваєте себе?",
                                        "Дуже гарно, дякую! А як ваш день пройшов?",
                                        "Чудово, як ваш день пройшов?",
                                        "Чудово! А у вас?",
                                        "Супер",
                                        "Гарний запитання. Потрібно буде це обдумати",
                                        "Непогано, спасибі за турботу!",
                                        "Прекрасно відпочиваю, як ваші справи?",
                                        "Захоплюючий день! Як у вас?",
                                        "Фантастично, дякую за запитання!",
                                        "Добре, дякую за ваші побажання!",
                                        "Прекрасно відпочиваю! Як у вас діла?",
                                        "Відмінно! Що нового?",
                                        "Запитуйте що завгодно, я завжди на зв'язку!",
                                        "Дуже добре! Як ваш день пройшов?",
                                        "Чудово проводжу час! А в вас як?",
                                        "Хороший настрій! А як у вас?",
                                        "Все гаразд, дякую за турботу!",
                                        "Феноменально! Чим можу допомогти?",
                                        "Добре відпочиваю, спасибі за запитання!",
                                        "Шикарно проводжу час! Як ви?",
                                        "Прекрасний настрій! А ви як?",
                                        "Відмінно почуваюся! Чи є що покращити?",
                                        "Відмінно! Як ви себе почуваєте?"
                                                                        ]

                    answer = random.choice(random_answers)
                if "увімкни пісн" in question or "відкрий плей-ліст" in question or "відкрий пллей-ліст" in question:
                    self.play_tts("Увімкню вашу улюблену музику")
                    self.start_music()
                if "трішки вперед" in question or "перемотати вперед" in question:
                    pyautogui.hotkey("ctrl", "right")
                    pyautogui.hotkey("right")
                    pyautogui.hotkey("right")
                    pyautogui.hotkey("right")
                    pyautogui.hotkey("right")
                if "трішки назад" in question or "перемотати назад" in question:
                    pyautogui.hotkey("ctrl", "left")
                    pyautogui.hotkey("left")
                    pyautogui.hotkey("left")
                    pyautogui.hotkey("left")
                    pyautogui.hotkey("left")
                if 'покрути монету' in question or 'підкинь монетку' in question or 'покрутив монетку' in question:
                    answer = random.choice(['Вам випав орел', 'Вам випала решка'])
                if "зроби" and "голосніше" in question or "зробити голосніше" in question:
                    [pyautogui.press('volumeup') for _ in range(4)]
                if "збільшити гучність" in question or "підвищити звук" in question:
                    [pyautogui.press('volumeup') for _ in range(10)]
                if "зроби тихіше" in question:
                    [pyautogui.press('volumedown') for _ in range(4)]
                if "зменшити гучність" in question or "понизити звук" in question:
                    [pyautogui.press('volumedown') for _ in range(10)]
                if "вимкни звук" in question or "постав на беззвучний" in question:
                    pyautogui.press('volumemute')
                if "гучність на" in question:

                    num_words_to_digits = {
                        "один": 1,
                        "два": 2,
                        "три": 3,
                        "чотири": 4,
                        "п'ять": 5,
                        "шість": 6,
                        "сім": 7,
                        "вісім": 8,
                        "дев'ять": 9,
                        "десять": 10,
                        "одинадцять": 11,
                        "дванадцять": 12,
                        "тринадцять": 13,
                        "чотирнадцять": 14,
                        "п'ятнадцять": 15,
                        "шістнадцять": 16,
                        "сімнадцять": 17,
                        "вісімнадцять": 18,
                        "дев'ятнадцять": 19,
                        "двадцять": 20,
                        "тридцять": 30,
                        "сорок": 40,
                        "п'ятдесят": 50,
                        "шістдесят": 60,
                        "сімдесят": 70,
                        "вісімдесят": 80,
                        "дев'яносто": 90,
                        "сто": 100,
                    }

                    def get_audio_volume_interface():
                        devices = AudioUtilities.GetSpeakers()
                        interface = devices.Activate(
                            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                        return cast(interface, POINTER(IAudioEndpointVolume))

                    # Функція для зміни гучності на вказаний рівень
                    def set_system_volume(volume_level):
                        # Обмежуємо рівень гучності у межах від 0 до 100
                        volume_level = max(0, min(volume_level, 100))
                        # Перетворюємо відсоток у діапазон від 0.0 до 1.0
                        volume_level_scalar = volume_level / 100.0
                        audio_interface = get_audio_volume_interface()
                        audio_interface.SetMasterVolumeLevelScalar(volume_level_scalar, None)
                    # Функція для перетворення числових слів у відповідні числа
                    def words_to_number(words):
                        total = 0
                        for word in words.split():
                            if word in num_words_to_digits:
                                total += num_words_to_digits[word]
                        return total

                    try:
                        # Виділяємо числові слова з рядка і перетворюємо їх у числа
                        volume_level_words = question.split("гучність на")[-1].strip()
                        volume_level = words_to_number(volume_level_words)
                        # Встановлюємо гучність
                        set_system_volume(volume_level)
                        answer = "Гучність успішно змінено"
                    except ValueError:
                        answer = "Некоректне значення для гучності."
                if self.question_contains(
                    question.lower(),
                    ["скільки часу", "скільки зараз часу", "котра година", "котра зараз година",
                    "скільки час", "скільки зараз час", "яка година", "котра година", "який зараз час"]
                ):
                    answer = self.tell_current_time()
                if "який сьогодні день" in question:
                    answer = self.tell_current_day()

                
                if "пошуковий рядок" in question or "пошукову стрічку" in question or "пошукова стрічка" in question:
                    keyboard.press_and_release('Ctrl+L')
                
                if "нову вкладку" in question or "нова вкладка" in question:
                    keyboard.press_and_release('ctrl+t')
                if "весь екран" in question:
                    keyboard.press_and_release('f')
                

                if 'відкрий ютуб' in question:
                    webbrowser.open('https://www.youtube.com/')
                if 'відкрий пром' in question:
                    webbrowser.open('https://prom.ua/')
                if 'відкрий розетк' in question:
                    webbrowser.open('https://rozetka.com.ua/')
                if 'відкрий приватбанк' in question or 'відкрий приватбанк' in question:
                    webbrowser.open('https://privatbank.ua/')
                if 'відкрий оглядач' in question:
                    webbrowser.open('https://www.obozrevatel.com/')
                if 'відкрий авто' in question:
                    webbrowser.open('https://auto.ria.com/')
                if 'відкрий каст' in question:
                    webbrowser.open('https://kasta.ua/')
                if 'відкрий замовлення' in question:
                    webbrowser.open('https://zakaz.ua/')
                if 'відкрий цитрус' in question:
                    webbrowser.open('https://www.citrus.ua/')
                if 'відкрий алло' in question:
                    webbrowser.open('https://allo.ua/')
                if 'відкрий фокстрот' in question:
                    webbrowser.open('https://www.foxtrot.com.ua/')
                if 'відкрий закупки' in question:
                    webbrowser.open('https://zakupki.prom.ua/')
                if 'відкрий водафон' in question:
                    webbrowser.open('https://www.vodafone.ua/')
                if 'відкрий київстар' in question:
                    webbrowser.open('https://kyivstar.ua/')
                if 'підібрати рецепт' in question:
                    webbrowser.open("https://retsepty.online.ua/podbor-retsepta/")
                if "погода на" in question:
                    answer = "Якщо ви хочете дізнатися погоду, скажіть у форматі 'яка погода в місті Київ'"
                if self.question_contains(
                    question.lower(),
                    ["наступну вкладку", "наступну сторінку", "наступної вкладки", "наступної сторінки", "наступна вкладка", "наступна сторінка"]
                ):
                    keyboard.press_and_release('ctrl+tab')
                if self.question_contains(
                    question.lower(),
                    ["попередню вкладку", "попередню сторінку", "попередньої вкладці", "попередньої сторінці",
                    "попередня вкладка", "попередня сторінка"]
                ):
                    keyboard.press_and_release('ctrl+shift+tab')
                if "закрий вкладку" in question or "закрий сторінку" in question:
                    keyboard.press_and_release('ctrl+w')
                if self.question_contains(
                    question.lower(),
                    ["доброго дня", "добрий день", "добрий вечір", "доброго вечора", "доброго ранку", "доброго ранку"]
                ):
                    answer = self.answer_greetings()
                if "погода в місті" in question:
                    search_term = re.search('погода в місті (.+)', question)
                    if search_term:
                        city = process_city_name(search_term.group(1))
                        date = get_date()
                        self.play_tts(get_weather(city, date))

                if "диспетчер завдань" in question or "диспетчер завдань" in question:
                    os.system('taskmgr')
                if "диспетчер пристроїв" in question:
                    os.system('devmgmt.msc')

                if "згорни вікно" in question.lower() or "згорни поточне вікно" in question.lower():
                    pyautogui.keyDown('win')
                    time.sleep(0.5)
                    pyautogui.press('down')
                    time.sleep(0.5)
                    pyautogui.press('down')
                    time.sleep(0.5)
                    pyautogui.keyUp('win')
                if "закрий вікно" in question.lower() or "закрий поточне вікно" in question.lower():
                    pyautogui.hotkey('alt', 'f4')
                    answer = "Закриваю поточне вікно"
                if "відкрий хром" in question.lower() or "відкрий гугл" in question.lower() or "відкрий браузер" in question.lower():
                    webbrowser.open("https://www.chrome.com")
                    answer = "Відкриваю Google Chrome - браузер гугл"
                if "відкрий студіо к" in question.lower():
                    try:
                        os.startfile('code')
                        answer = "Додаток Visual Studio Code - віжуал студіо код відкрито"
                    except FileNotFoundError:
                        pass
                        answer = "Додаток Visual Studio Code - віжуал студіо код не встановлено"
                if "відкрий калькулятор" in question.lower():
                    try:
                        os.startfile('calc')
                        answer = "Додаток Калькулятор відкрито"
                    except FileNotFoundError:
                        answer = "Додаток Калькулятор не встановлено"
                if "відкрий блокнот" in question.lower():
                    try:
                        os.startfile('notepad')
                        answer = "Додаток Блокнот відкрито"
                    except FileNotFoundError:
                        answer = "Додаток Блокнот не встановлено"
                if "відкрий пейнт" in question.lower():
                    try:
                        os.startfile('mspaint')
                        answer = "Додаток Паєнт відкрито"
                    except FileNotFoundError:
                        answer = "Додаток Паєнт не встановлено"
                if "файловий менеджер" in question.lower():
                    try:
                        os.system('explorer.exe')
                        answer = "Файловий менеджер відкрито"
                    except FileNotFoundError:
                        answer = "Файловий менеджер не знайдено"
                if "закрий файловий менеджер" in question.lower():
                    try:
                        os.system('taskkill /im explorer.exe /f')
                        answer = "Додаток файловий менеджер закрито"
                    except FileNotFoundError:
                        answer = "Додаток файловий менеджер не був відкритий"
                if "закрий хром" in question.lower() or "закрий гугл" in question.lower() or "закрий браузер" in question.lower():
                    try:
                        os.system('taskkill /im chrome.exe /f')
                        answer = "Додаток Google Chrome закрито"
                    except FileNotFoundError:
                        answer = "Додаток Google Chrome не був відкритий"
                if "закрий студіо код" in question.lower():
                    try:
                        os.system('taskkill /im code.exe /f')
                        answer = "Додаток Visual Studio Code закрито"
                    except FileNotFoundError:
                        answer = "Додаток Visual Studio Code не був відкритий"
                if "закрий калькулятор" in question.lower():
                    try:
                        os.system('taskkill /im calc.exe /f')
                        answer = "Додаток Калькулятор закрито"
                    except FileNotFoundError:
                        answer = "Додаток Калькулятор не був відкритий"
                if "закрий блокнот" in question.lower():
                    try:
                        os.system('taskkill /im notepad.exe /f')
                        answer = "Додаток Блокнот закрито"
                    except FileNotFoundError:
                        answer = "Додаток Блокнот не був відкритий"

                if "закрий пейнт" in question.lower():
                    try:
                        os.system('taskkill /im mspaint.exe /f')
                        answer = "Додаток Paint закрито"
                    except FileNotFoundError:
                        answer = "Додаток Paint не був відкритий"
                if "закрий ексель" in question.lower():
                    try:
                        os.system('taskkill /im excel.exe /f')
                        answer = "Додаток Excel закрито"
                    except FileNotFoundError:
                        answer = "Додаток Excel не був відкритий"

                if "нове вікно" in question.lower():
                    keyboard.press('ctrl')
                    time.sleep(0.1)  # Затримка 0.1 секунди
                    keyboard.press_and_release('n')
                    keyboard.release('ctrl')

                if "новий робочий стіл" in question.lower():
                    pyautogui.hotkey('win', 'ctrl', 'd')

                if "олів та застосунків" in question.lower():

                    pyautogui.hotkey('win', 'tab')

                if "наступний робочий стіл" in question.lower():
                    pyautogui.hotkey('win', 'ctrl', 'right')

                if "попередній робочий стіл" in question.lower():
                    pyautogui.hotkey('win', 'ctrl', 'left')

                

                if 'оновити сторінку' in question:
                    pyautogui.press('f5')
                    answer = 'Сторінка оновлена.'
                
                if "відкрий історію" in question:
                    keyboard.press_and_release('ctrl+h')

                if "закриту вкладку" in question or "поверни вкладку" in question:
                    keyboard.press_and_release('Ctrl+Shift+T')

                if "зберегти" in question or "збережи" in question:
                    keyboard.press_and_release('Ctrl+S')
                    answer = "Кнопку 'Зберегти' натиснуто."

                
                if "закрий всі вікна" in question or "закрий вікна" in question:
                    keyboard.press_and_release('Win+D')

                if "закрий панель керування" in question:
                    os.system('TASKKILL /F /IM "control.exe"')
                if "закрий параметри" in question:
                    os.system("taskkill /im SystemSettings.exe /f")

                if "буфер обміну" in question:
                    keyboard.press_and_release('Win+V')

                if "панель керування" in question:
                    os.system("control")
                    time.sleep(0)
                    answer = "Панель керування відкрита."

                if "увімкни параметр" in question or "відкрий параметр" in question or "відкрити параметр" in question or "увімкнути параметр" in question:
                    keyboard.press_and_release('Win+I')
                    time.sleep(1)
                    answer = "Параметри відкрито."

                if "закр" in question and "вікно" in question:
                    keyboard.press_and_release('Alt+F4')

                


                if "розкажи жарт" in question or "розкажи анекдот" in question:
                    jokes=[
                        "Якщо ти відчуваєш себе непотрібним, згадай, що і батарейки в пульті дистанційного керування мають своє значення.",
                        "Моє вчорашнє дієтичне меню: на сніданок - каша, на обід - салат, на вечерю - відчай.",
                        "Завжди дивно, коли діти кажуть, що дорослі не розуміють їх. Тим часом, дорослі відчувають себе як діти на роботі, коли вони намагаються включити принтер.",
                        "Чому програмісти не люблять грати в хованки? Бо навіть в ігрі намагаються знайти себе в пошуках.",
                        "Якщо говорити про дітей, то годувати їх вони вміють вже з 6 місяців, а догодувати - до самого весілля.",
                        "Щодо дієти: кажуть, що важко схуднути. Не правда. Важко триматися на дієті, коли в кожному куточку тебе чекає щось смачненьке.",
                        "Деякі люди думають, що щасливе життя - це коли у тебе багато грошей. Але я вважаю, що щасливе життя - це коли ти не вмієш рахувати до десяти, не говорячи вже про гроші.",
                        "Якщо у вас є вільні 10 хвилин, пройдіться по магазину з електронікою. Через 5 хвилин ви будете виглядати, як батько, який зрозумів, що йому потрібна нова іграшка.",
                        "Життя подібне до шахів: якщо воно тобі подарувало коня, зазвичай воно тобі відбирає декілька пішаків.",
                        "Моя найбільша слабкість - це кава. Але не та кава, що я п'ю. Та кава, яку я переливаю собі на штани, коли п'ю.",
                        "Зробивши затишок у залі, вирушаєш в ліжко, але заснути не можеш. Ось так я і знайшов себе, лежачи в ліжку о 3 годині ночі, думаючи про те, чому бджоли вирішили вибирати саме вулики як свої домівки.",
                        "Життя - це не картопля. Ти не можеш врізати його, підсмажити і з'їсти. Ти можеш тільки врізати, підсмажити і з'їсти картоплю.",
                        "Чому програмісти так люблять різдвяні та новорічні канікули? Бо ті декілька днів, коли всі говорять про код, вони можуть зайнятися своїми справами.",
                        "Якщо кажуть, що любов здатна на все, це не означає, що ви зможете отримати замісників на роботі, коли ви вирішили провести весь день з коханою людиною.",
                        "Коли я говорю, що в мене є ідеальне тіло, я маю на увазі, що воно ідеально підходить для сну та відпочинку."
                    ]

                    answer = random.choice(jokes)

                if "сторінку завантажень" in question or "сторінка завантажень" in question or "відкрий завантаження" in question:
                    keyboard.press('ctrl')
                    time.sleep(0.1)  # Затримка 0.1 секунди
                    keyboard.press_and_release('j')
                    keyboard.release('ctrl')
                if "налаштування облікового запису" in question:
                    subprocess.Popen('explorer.exe ms-settings:emailandaccounts')
                if "налаштування конфіденційності" in question:
                    subprocess.Popen('explorer.exe ms-settings:privacy')
                if "налаштування оновлення та безпеки" in question:
                    subprocess.Popen('explorer.exe ms-settings:windowsupdate')
                if "налаштування зберігання" in question:
                    subprocess.Popen('explorer.exe ms-settings:storagesense')
                if "налаштування мобільного гарячого кінця" in question:
                    subprocess.Popen('explorer.exe ms-settings:mobilehotspot')
                if "налаштування мережі та інтернету" in question:
                    subprocess.Popen('explorer.exe ms-settings:network')
                if "налаштування служби віддаленого робочого столу" in question:
                    subprocess.Popen('explorer.exe ms-settings:remotedesktop')
                if "налаштування сповіщення" in question or "налаштування сповіщень" in question:
                    subprocess.Popen('explorer.exe ms-settings:notifications')
                if "налаштування екранної клавіатури" in question:
                    subprocess.Popen('explorer.exe ms-settings:easeofaccess-keyboard')
                if "налаштування сім'ї та інших користувачів" in question:
                    subprocess.Popen('explorer.exe ms-settings:otherusers')
                if "налаштування часу та мови" in question:
                    subprocess.Popen('explorer.exe ms-settings:dateandtime')
                if "налаштування режиму геймпада" in question:
                    subprocess.Popen('explorer.exe ms-settings:gaming-gamecontroller')
                if "налаштування кольору" in question:
                    subprocess.Popen('explorer.exe ms-settings:personalization-colors')
                if "налаштування теми" in question:
                    subprocess.Popen('explorer.exe ms-settings:personalization-themes')
                if "налаштування робочого столу" in question:
                    subprocess.Popen('explorer.exe ms-settings:personalization-start')
                if "налаштування заставки" in question:
                    subprocess.Popen('explorer.exe ms-settings:lockscreen')
                if "налаштування батьківського контролю" in question:
                    subprocess.Popen('explorer.exe ms-settings:otherusers')
                if "налаштування акумулятора" in question:
                    subprocess.Popen('explorer.exe ms-settings:batterysaver')
                if "налаштування застосунків за замовчуванням" in question:
                    subprocess.Popen('explorer.exe ms-settings:appsdefaultapps')
                if "налаштування безпеки і відновлення" in question:
                    subprocess.Popen('explorer.exe ms-settings:recovery')
                if "налаштування мікрофону" in question:
                    subprocess.Popen('explorer.exe ms-settings:privacy-microphone')
                if "налаштування камери" in question:
                    subprocess.Popen('explorer.exe ms-settings:privacy-webcam')
                if "налаштування особистої інформації" in question:
                    subprocess.Popen('explorer.exe ms-settings:yourinfo')
                if "налаштування автозапуску" in question:
                    subprocess.Popen('explorer.exe ms-settings:startupapps')
                if "налаштування доступності" in question:
                    subprocess.Popen('explorer.exe ms-settings:easeofaccess-highcontrast')
                if "налаштування варіантів входу" in question:
                    subprocess.Popen('explorer.exe ms-settings:signinoptions')

                
                if "привіт" in question or "здоров" in question or "доброго дня" in question or "добрий вечір" in question or "вітаю" in question:
                    current_time = datetime.datetime.now()
                    hour = current_time.hour
                    if 4 <= hour < 12:
                        greetings = ["Доброго ранку", "Доброго дня", "Доброго часу доби", "Привіт"]
                        answer = random.choice(greetings)
                    elif 12 <= hour < 16:
                        greetings = ["Доброго дня", "Вітаю", "Доброго часу доби", "Привіт"]
                        answer = random.choice(greetings)
                    elif 16 <= hour < 23:
                        greetings = ["Доброго вечора", "Як справи?", "Доброго часу доби", "Привіт"]
                        answer = random.choice(greetings)
                    else:
                        answer = "Доброї ночі. Зараз пізньо вечора, краще поспіть."
                if "закрий калькулятор" in question.lower() or any(
                            fuzz.ratio("закрий калькулятор", word.lower()) >= 80 for word in question.split()):
                        try:
                            os.system('taskkill /f /im calc.exe')
                            answer = "Додаток калькулятор закрито."
                        except FileNotFoundError:
                            answer = "Додаток калькулятор не знайдено."
                if "закрий блокнот" in question.lower() or any(
                        fuzz.ratio("закрий блокнот", word.lower()) >= 80 for word in question.split()):
                    try:
                        os.system('taskkill /f /im notepad.exe')
                        answer = "Додаток блокнот закрито."
                    except FileNotFoundError:
                        answer = "Додаток блокнот не знайдено."


                if "зроби скріншот" in question:
                    current_time = datetime.datetime.now()
                    time_string = current_time.strftime("%Y-%m-%d_%H-%M-%S")
                    screenshot = ImageGrab.grab()
                    file_name = f"screenshot_{time_string}.png"
                    screenshot.save(file_name)
                    print(f"Скріншот збережено в файл: {file_name}")
                    answer = "Скріншот створено успішно"

                if "зроби фото" in question:

                    image_folder = "C:/images"

                    for folder in ['изображения', 'зображення', 'images']:
                        if os.path.exists(folder):
                            image_folder = folder
                            break

                    if not image_folder:
                        os.mkdir('images')
                        image_folder = 'images'

                    # Получаем список файлов в текущей папке
                    current_folder_path = os.path.join(os.getcwd(), image_folder)
                    if not os.path.exists(current_folder_path):
                        os.mkdir(current_folder_path)

                    current_folder_files = [f for f in os.listdir(current_folder_path) if
                                            os.path.isfile(os.path.join(current_folder_path, f))]

                    # Создаем имя нового файла на основе текущего времени
                    current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                    new_file_name = current_time + '.jpg'

                    # Подключаемся к камере
                    camera = cv2.VideoCapture(0)

                    # Проверяем, найдена ли камера
                    if not camera.isOpened():
                        answer = 'Помилка: камера не знайдена'
                    else:
                        # Делаем фото и сохраняем в папке с изображениями
                        success, image = camera.read()
                        if success:
                            path = os.path.join(current_folder_path, new_file_name).replace("\\", "/")
                            cv2.imwrite(path, image)
                            answer = 'Фото успішно збережено'
                        else:
                           answer = 'Помилка: фото не було збережено'

                        camera.release()

                if "зміна мови" in question or "зміни мову" in question or "змінити мову" in question:
                    keyboard.press_and_release('Alt+Shift')
                    answer = 'мова змінена'

                elif "пошук елементу" in question or "знайти елемент" in question:
                    keyboard.press_and_release('Ctrl+f')

                elif "вікіпедія" in question:
                    search_term = re.search('вікіпедія (.+)', question)
                    if search_term:
                        search_term = search_term.group(1).replace(' ', '_')
                        wiki_url = f"https://uk.wikipedia.org/wiki/{search_term}"
                        webbrowser.open(wiki_url)

                # elif "хто ти" in question:
                #     answer = "Я голосовий помічник Арт."
                elif "знайди" in question.lower() and "відео" not in question.lower():
                    search_query = "+".join(question.split()[1:])
                    url = "https://www.google.com/search?q=" + search_query
                    response = requests.get(url)

                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        search_results = soup.find_all('div', class_='BNeawe')

                        if search_results:
                            first_result = search_results[0].text
                            # Замінюємо англійські літери на українські
                            translated_result = ''.join(letter_mapping.get(c.lower(), c) for c in first_result)
                            # Перевіряємо, чи є числа у першому результаті та переводимо їх у текст
                            words = translated_result.split()
                            for i, word in enumerate(words):
                                if word.isdigit():
                                    words[i] = num2words(int(word), lang='uk')  # Перетворюємо число у текст
                            answer = ' '.join(words)
                        else:
                            answer = "Не вдалося знайти інформацію за вашим запитом."

                    else:
                        answer = "Помилка при отриманні результатів пошуку."

                    webbrowser.open(url)
                
                elif self.question_contains(
                    question.lower(), ["завершення програми", "завершити програму"]
                ):
                    answer = "завершую програму"
                    self.play_tts(answer)
                    self.exit_app()

                elif "яскравість на" in question:
                    set_monitor_brightness(question)

                elif "напиши" in question:
                    self.enter_request("напиши", question)
                elif "напише" in question:
                    self.enter_request("напише", question)
                elif "повтори за мною" in question:
                    answer = self.repeat_after_me("повтори за мною", question)
                elif "повтори" in question:
                    answer = self.repeat_after_me("повтори", question)
                elif "натисни" in question:
                    x, y = pyautogui.position()
                    pyautogui.click(x, y)
                

                # elif "проаналізу" in question:
                #     text_command = question
                #     result = process_command(text_command)
                #     answer = result

                elif "пароль вай-фай" in question:
                    def get_connected_wifi_info():
                        try:
                            output = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces'], shell=True, universal_newlines=True)
                            connected_network = re.search(r'SSID\s*:\s(.*)', output).group(1)

                            password = get_wifi_password(connected_network)
                            return connected_network, password
                        except subprocess.CalledProcessError:
                            return None, None

                    def get_wifi_password(profile_name):
                        try:
                            output = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', f'name="{profile_name}"', 'key=clear'], shell=True, universal_newlines=True)
                            key_index = output.find("Key Content")
                            if key_index != -1:
                                start_index = output.find(":", key_index) + 2
                                end_index = output.find("\n", start_index)
                                password = output[start_index:end_index]
                                return password.strip()
                            else:
                                return None
                        except subprocess.CalledProcessError:
                            return None

                    def copy_to_clipboard(password):
                        pyperclip.copy(password)

                    def main():
                        connected_network, connected_wifi_password = get_connected_wifi_info()

                        root = tk.Tk()
                        root.title("Пароль від підключеної Wi-Fi мережі")

                        if connected_network and connected_wifi_password:
                            label_network = tk.Label(root, text=f"Підключена Wi-Fi мережа: {connected_network}", font=("Arial", 12), fg="blue")
                            label_network.pack(pady=10)

                            label_password = tk.Label(root, text=f"Пароль від мережі '{connected_network}': {connected_wifi_password}", font=("Arial", 12), fg="green")
                            label_password.pack(pady=10)

                            copy_button = tk.Button(root, text="Копіювати пароль", font=("Arial", 12), bg="lightblue", command=lambda: copy_to_clipboard(connected_wifi_password))
                            copy_button.pack(pady=10)
                        else:
                            label_error = tk.Label(root, text="Сталася помилка під час отримання інформації про підключену Wi-Fi мережу", font=("Arial", 12), fg="red")
                            label_error.pack(pady=10)

                        root.mainloop()

                    def run_gui():
                        Thread(target=main).start()

                    if __name__ == "__main__":
                        run_gui()

                elif "документація проекту" in question or "команди асистента" in question:

                    # Створення вікна
                    window = tk.Tk()
                    window.title("Команди голосового асистента")

                    # Додавання тексту
                    text = """
                    Керування звуком:

                    -Зроби тихіше | -8 від гучності (+)
                    -Зроби голосніше | +8 до гучності (+)
                    -Вимкни звук \ постав на беззвучний (+)
                    -Збільшити гучність \ підвищити звук | +20 до гучності (+)
                    -Зменшити гучність \ понизити звук | -20 від гучності (+)
                    -Гучність на [значення] (+)

                    Керування яскравістю:

                    -Зроби яскравіше \ підвищи\збільш\підніми яскравість | +8 до яскравості (+)
                    -Зроби тьмяніше \ знизь\зменши\опусти яскравість | -8 до яскравості (+)
                    -Яскравість на [значення]

                    Керування вікнами:

                    -Закрий вікно \ закрий поточне вікно
                    -Згорни вікно
                    -Нове вікно
                    -Відкрий нове вікно
                    -Закрий всі вікна
                    -Нова вкладка \ відкрий нову вкладку (+)
                    -Наступна вкладка (+)
                    -Попередня вкладка (+)
                    -Закрий вкладку (+)

                    Мультимедіа:

                    -Увімкни пісню (+)
                    -Відкрий плей-лист (+)
                    -Перемотати вперед \ трішки вперед (+)
                    -Перемотати назад \ трішки назад (+)
                    -Пауза\Відтворення

                    Пошук:

                    -Знайди елемент \ пошук елементу
                    -Знайди [ваш запит] (знаходить інформацію у браузері, по можливості озвучує)
                    -Вікіпедія [ваш запит]

                    Данні:

                    -Скільки часу \ яка\котра година \ який зараз час (+)
                    -Який сьогодні день (+)
                    -Кількість ядер (пристрою)
                    -Пароль вай-фай

                    Інформація:

                    -Погода в місті [назва]  (+)
                    -Новини
                    -Хто такий [ваш запит]
                    -Що таке [ваш запит]
                    -Вікіпедія [ваш запит] 

                    Система (+):

                    -Зміна мови \ змінити мову
                    -Новий робочий стіл
                    -Попередній\наступний робочий стіл
                    -Меню столів та застосунків
                    -Буфер обміну
                    -Панель керування
                    -Відкрити\увімкнути параметри
                    -Перезавантажити пристрій
                    -Вимкнути пристрій
                    -Диспетчер завдань
                    -Диспетчер пристроїв
                    -Налаштування облікового запису
                    -Налаштування конфіденційності
                    -Налаштування оновлення та безпеки
                    -Налаштування зберігання
                    -Налаштування мобільного гарячого кінця
                    -Налаштування мережі та Інтернету
                    -Налаштування служби віддаленого робочого столу
                    -Налаштування сповіщення
                    -Налаштування екранної клавіатури
                    -Налаштування сім'ї та інших користувачів
                    -Налаштування часу та мови
                    -Налаштування режиму геймпада
                    -Налаштування кольору
                    -Налаштування теми
                    -Налаштування робочого столу
                    -Налаштування заставки
                    -Налаштування батьківського контролю
                    -Налаштування акумулятора
                    -Налаштування застосунків за замовчуванням
                    -Налаштування безпеки і відновлення
                    -Налаштування особистої інформації
                    -Налаштування мікрофону
                    -Налаштування камери
                    -Налаштування автозапуску
                    -Налаштування доступності
                    -Налаштування варіантів входу

                    Браузер:

                    -Повноекранний режим \ вихід з повноекранного режиму
                    -Сторінка завантажень (+)
                    -Оновити сторінку
                        
                        Cайти:
                            -Відкрий пошту \ відкрий електронну пошту (+)
                            -Відкрий\увімкни фільми (+)
                            -Відкрий ютуб (+)
                            -Відкрий пром (+)
                            -Відкрий розетку (+)
                            -Відкрий приватбанк (+)
                            -Відкрий обозрювач (+)
                            -Відкрий авто (+)
                            -Відкрий касту (+)
                            -Відкрий замовлення (+)
                            -Відкрий цитрус (+)
                            -Відкрий алло (+)
                            -Відкрий фокстрот (+)
                            -Відкрий закупки (+)
                            -Відкрий водафон (+)
                            -Відкрий київстар (+)
                            -Підібрати рецепт (+)

                    Вказівник миші:

                    -Вгору\вище
                    -Вниз\нижче
                    -Праворуч\правіше
                    -Ліворуч\лівіше

                    Програми:

                        Відкрий (+):
                        -Фотошоп (adobe)
                        -Ексель
                        -Браузер\хром
                        -Пойнт (powerpoint)
                        -Кошик
                        -Документ (word)
                        -Телеграм
                        -Блокнот
                        -Калькулятор
                        -Студіо код (Vs code)
                        -Файловий менеджер
                        Закрий (+):
                        -Документ
                        -Блокнот
                        -Калькулятор
                        -Панель керування
                        -Параметри
                        -Ексель
                        -Пейнт
                        -Студіо код
                        -Браузер\гугл\хром
                        -Файловий менеджер

                    Загальне:

                    -Зберегти
                    -Виділити
                    -Вставити
                    -Копіювати
                    -Видалити
                    -Скасувати
                    -Натисни
                    -Далі\ентер
                    -Пошуковий рядок

                    Розмовне:

                    -Доброго дня\привіт\вітаю.. (+)
                    -Як справи (+)
                    -Як тебе звати
                    -Що робиш
                    -Як тебе звати
                    -Спасибі
                    -Повтори за мною [текст] 
                    -Повтори [текст] 
                    -Розкажи жарт\анекдот (+)

                    Інші:

                    -Покрути\підкинь монету (+)
                    -Зроби фото
                    -Зроби скріншот
                    -Знайди відео [ваш запит]
                    -Напиши [текст]

                    Завершити програму \ завершення програми

                    Увага:
                        1.Команди позначені (+) означають що їх можна використовувати по декілька в одному запиті\звернені до асистента, інші команди які цього не мають спрацюють у випадку якщо це одна команда в запиті, або ж якщо ця команда остання в звернені
                        2. Команди "зроби фото" та "зроби скріншот" зберігають свої данні у папці C:\images, якщо ж такої немає то створюють. Також цей файл може створюватись у директорії де знаходиться асистент
                    """

                    # Створення текстового поля зі скроллбаром
                    scrollbar = tk.Scrollbar(window)
                    scrollbar.pack(side='right', fill='y')

                    text_box = tk.Text(window, wrap='word', yscrollcommand=scrollbar.set, font=('Courier', 10))
                    # text_box.tag_configure("salad", foreground="green")
                    text_box.insert('1.0', text, "salad")  # Додаємо тег "salad" при вставці тексту
                    text_box.pack(expand=True, fill='both')

                    # Встановлюємо текстове поле у режим "disabled", щоб заборонити редагування
                    text_box.config(state='disabled')

                    # Пов'язуємо скроллбар і текстове поле
                    scrollbar.config(command=text_box.yview)

                    # Запуск циклу графічного інтерфейсу
                    window.mainloop()

                elif any(keyword in question for keyword in ["увімкни відео", "відкрий відео", "запусти відео", "знайди відео"]):
                    query = question.split(" ", 2)[-1]
                    url = f"https://www.youtube.com/results?search_query={query}"
                    webbrowser.open(url)
                    time.sleep(3)
                    keyboard.press_and_release('enter')
                elif "субтитри" in question:
                    pyautogui.sleep(1)
                    pyautogui.press('C')


                elif "відкрий документ" in question.lower():
                    try:
                        os.startfile('winword')
                        answer = "Додаток документи відкрито"
                    except FileNotFoundError:
                        pass
                        answer = "Додаток документи не встановлено"
                elif "закрий документ" in question.lower():
                    try:
                        # Виконуємо команду для закриття процесу Microsoft Word
                        exit_code = os.system('taskkill /im winword.exe /f')
                        # Перевіряємо вихідний код команди taskkill
                        if exit_code == 0:
                            answer = "Додаток документ закрито"
                        else:
                            answer = "Додаток документ не був відкритий або не вдалося його закрити"
                    except Exception as e:
                        answer = "Додаток документ не був відкритий"

                elif "відкрий" in question.lower() and ("кошик" in question.lower() or "корзину" in question.lower()):
                    os.system('explorer.exe shell:RecycleBinFolder')


                elif "відкрий телеграм" in question.lower():
                    try:
                        os.system("telegram.exe")
                    except FileNotFoundError:
                        pass
                        answer = "Додаток Телеграм не встановлено"
                elif "відкрий пойнт" in question.lower() or "відкрий поверпоінт" in question.lower():
                    try:
                        os.startfile('powerpnt')
                        answer = "Додаток Пауерпоінт відкрито"
                    except FileNotFoundError:
                        pass
                        answer = "Додаток Пауерпоінт не встановлено"
                elif "відкрий ексель" in question.lower():
                    try:
                        os.startfile('excel')
                        answer = "Додаток Ексель відкрито"
                    except FileNotFoundError:
                        pass
                        answer = "Додаток Ексель не встановлено"
                elif "відкрий" and "фотошоп" in question.lower():
                    try:
                        os.system('Photoshop.exe')
                        answer = "Додаток Adobe Photoshop відкрито"
                    except FileNotFoundError:
                        pass
                        answer = "Додаток Adobe Photoshop не встановлено"
                elif "кількість ядер" in question or "скільки ядер" in question:
                    num_cores = os.cpu_count()
                    num_cores_words = num2words(num_cores, lang='uk')
                    answer = "Кількість ядер вашого пристрою: " + num_cores_words
                
                elif "спасибі" in question or "дякую" in question or "пасибо" in question:
                    answers = [
                        "З задоволенням!",
                        "Не потрібно подяки!",
                        "Рада допомогти!",
                        "Завжди готова допомогти!",
                        "Будь ласка!",
                        "Це моя робота!",
                        "Не дякуйте!",
                        "Я рада бути корисною!",
                        "Необхідно чи будувати робота?",
                        "Будь ласка, це моя задача!",
                        "Я завжди готовий допомогти!",
                        "З радістю допоможу вам!",
                        "З задоволенням роблю це для вас!",
                        "Не потрібно подяки, ваше задоволення - моє задоволення!",
                        "Я рада, що можу бути корисною!",
                        "Ніколи не відмовлюся від подяки!",
                        "Це привілегія бути вашим помічником!",
                        "Рада, що змогла допомогти вам!",
                        "Без проблем, це моя роль!",
                        "Була рада допомогти, звертайтеся в будь-який час!"
                    ]

                    # Вибір випадкової відповіді
                    answer = random.choice(answers)

                elif "новини" in question:
                    feed_url = 'https://www.pravda.com.ua/rss/view_news/'
                    try:
                        requests.get("http://www.google.com", timeout=3)
                    except requests.ConnectionError:
                        answer = "Відсутнє інтернет-з'єднання"
                        exit()

                    feed = feedparser.parse(feed_url)

                    if len(feed.entries) > 0:
                        entry = feed.entries[1]  # Отримання останніх новин
                        if 'title' in entry and 'link' in entry and 'description' in entry:
                            title = entry.title
                            link = entry.link
                            description = entry.description

                            # Видобуття тексту першого абзацу новини
                            start = description.find('<br>') + 4
                            end = description.find('<p>Читайте також:')
                            first_paragraph = description[start:end].replace('<p>', '').replace('</p>', '').strip()

                            # Переклад чисел у слова
                            words_in_paragraph = []
                            for word in first_paragraph.split():
                                if word.isdigit():
                                    words_in_paragraph.append(num2words(int(word), lang='uk'))
                                else:
                                    words_in_paragraph.append(word)
                            first_paragraph_translated = ' '.join(words_in_paragraph)

                            webbrowser.open(link)
                            # Озвучення заголовка новини
                            self.play_tts(title)

                            # Озвучення першого абзацу новини
                            self.play_tts(first_paragraph_translated)

                            pyautogui.keyDown('alt')
                            pyautogui.press('space')
                            pyautogui.press('n')
                            pyautogui.keyUp('alt')

                        else:
                            answer = "Немає доступних новин."

                elif "вгору" in question or "вище" in question:
                    pyautogui.scroll(600)
                elif "вниз" in question or "нижче" in question:
                    pyautogui.scroll(-600)
                elif "праворуч" in question or "правіше" in question:
                    pyautogui.hscroll(600)
                elif "ліворуч" in question or "лівіше" in question:
                    pyautogui.hscroll(-600)

                elif 'повноекранний режим' in question or 'вихід з повноекранного режиму' in question:
                    browser_window = gw.getWindowsWithTitle('Chrome')[0]
                    if browser_window.isActive:
                        pyautogui.press('f11')
                        answer = 'Виконую'
                    else:
                        answer = 'Ви повинні бути в браузері, щоб перейти в повноекранний режим.'

                elif 'пауза' in question or 'зупинка' in question or 'паузу' in question:
                    pyautogui.press('space')
                elif 'відтворення' in question:
                    pyautogui.press('space')
                elif "далі" in question or "ентер" in question or "детальніше" in question:
                    keyboard.press_and_release('enter')

                elif "виділи" in question or "виділити" in question:
                    keyboard.press_and_release('Ctrl+A')
                    answer = "Виділено."

                elif "встав" in question or "вставити" in question:
                    keyboard.press_and_release('Ctrl+V')
                    answer = "Кнопку 'Вставити' натиснуто."
                elif "копіювати" in question or "копіюй" in question:
                    keyboard.press_and_release('Ctrl+C')
                    answer = "Кнопку 'Вставити' натиснуто."

                elif "видалити" in question:
                    keyboard.press_and_release('backspace')

                elif "скасування" in question or "скасуй" in question or "скасувати" in question:
                    keyboard.press_and_release('Ctrl+Z')
                    keyboard.press_and_release('esc')
                    answer = "Дія скасована."
                elif question in ["перезавантаж пристрій", "перезавантаж комп'ютер", "перезавантаж ноутбук"]:
                    os.system("shutdown -r -t 5")
                    answer = "Виконую перезавантаження устаткування."

                elif question in ["вимкни пристрій", "вимкни комп'ютер", "вимкни ноутбук"]:
                    os.system("shutdown -s -t 3")
                    answer = "Виконую вимкнення устаткування."

                elif "що робиш" in question:
                    answer = "чекаю ваші команди"

                elif "як тебе звати" in question:
                    answer = "Мене звуть Арт."

                elif "хто такий " in question or "що таке " in question:
                    wikipedia.set_lang("uk")
                    try:
                        page = wikipedia.page(question)
                        summary = page.content.split('\n')[0]
                        summary = re.sub(r'\([^)]*\)', '', summary)  # виключаємо текст у дужках

                        # Перетворення чисел у слова
                        numbers = re.findall(r'\b\d+\b', summary)
                        for number in numbers:
                            word_number = num2words(int(number), lang='uk')
                            summary = summary.replace(number, word_number)

                        answer = summary
                    except wikipedia.exceptions.DisambiguationError as e:
                        print(f"Занадто багато можливих визначень для запиту \"{question}\". Спробуйте уточнити запит.")
                    except wikipedia.exceptions.PageError as e:
                        print(f"Не знайдено статей, що відповідають запиту \"{question}\".")
                    except Exception as e:
                        print(f"Сталася помилка: {e}")

                # elif " арт " in question:
                #     responses = ["Слухаю", "Що вам доручити?", "Я тут", "Не хвилюйтесь, я на місці", "До ваших послуг"]
                #     answer = random.choice(responses)


                if answer:
                    self.update_dialog(speaker='art', text=answer)
                    self.play_tts(answer)


            # time.sleep(0.1)

    def stop_dialog(self):
        if not self.run:
            return
        self.run = False
        self.play_tts('Голосовий помічник вимкнений')
        self.update_dialog(speaker='Art', text='Голосовий помічник вимкнено')
        self.dialog_button.clicked.disconnect()
        self.dialog_button.clicked.connect(self.start_dialog)

    def start_dialog(self):
        if self.run:
            return
        #self.speak_text('Слухаю')
        self.play_tts('Слухаю')
        self.run = True
        self.update_dialog(speaker='Art', text='Слухаю Вас…')
        self.dialog_button.clicked.disconnect()
        self.dialog_button.clicked.connect(self.stop_dialog)

    def start_assistant_process(self):
        self.dialog_process = threading.Thread(target=self.run_assistant)
        self.dialog_process_stop = False
        self.dialog_process.setDaemon(True)
        self.dialog_process.start()

    def open_telegram(self):
        webbrowser.open('https://t.me/voice_assistent')

    def get_geo_data(self):
        g = geocoder.ip('me')
        if g.ok:
            self.city = g.city
            self.country = g.country

    def set_geo_info(self):
        if not self.city or not self.country:
            self.get_geo_data()
        if self.city and self.country:
            self.geo_label.setText(self._translate(
                "MainWindow",
                "<html><head/><body><p><span style=\" font-size:10pt; "
                f"font-weight:600; color:#ffffff;\">{self.country}, {self.city}</span></p></body></html>"))
        else:
            self.geo_label.setText(self._translate(
                "MainWindow",
                "<html><head/><body><p><span style=\" font-size:8pt; "
                f"font-weight:600; color:#ffffff;\">Не могу определить локацию</span></p></body></html>"))

    def get_weather(self):
        g = geocoder.ip('me')
        city = g.city
        api_key = '78de1db61ffa6efd32239911ca57f068'
        weather_url = f"http://api.openweathermap.org/data/2.5/weather"
        # weather_url += f"?q={self.city}&appid={api_key}&lang=ru&units=metric"
        weather_url += f"?q={city}&appid={api_key}&lang=uk&units=metric"
        try:
            response = requests.get(weather_url)
            data = response.json()
        except requests.exceptions.ConnectionError:
            self.weather.update({'description': 'Нет интернет-соединения'})
        else:
            try:
                # Parse weather data to display relevant information
                self.weather['description'] = data['weather'][0]['description']
                self.weather['temp'] = round(data['main']['temp'])
                # feels_like = round(data['main']['feels_like'] - 273.15, 1)
                self.weather['wind_speed'] = round(data['wind']['speed'], 1)
                self.weather['humidity'] = data['main']['humidity']
                return
            except KeyError:
                if data['message'] == 'city not found':
                    self.weather.update({'description': 'Город не найден'})
                else:
                    logger.error(f'Unknown error while geeting weather info:\n{data}')

        self.weather.update({'temp': '?', 'wind_speed': '?', 'humidity': '?'})

    def set_weather_picture(self):
        description = self.weather['description']
        if 'дощ' in description:
            self.weather_pic = "C:/My-assistent/icons/rain.jpg"
        elif 'хма' in description or 'пасм' in description:
            self.weather_pic = "C:/My-assistent/icons/weather.jpg"
        elif 'сне' in description  or 'сні' in description:
            self.weather_pic = "C:/My-assistent/icons/snow.jpg"
        else:
            self.weather_pic = "C:/My-assistent/icons/sun.jpg"
        self.weather_pic_label.setPixmap(QtGui.QPixmap(self.weather_pic))
        self.weather_pic_label.setScaledContents(True)
        # image = Image.open(image_path)
        # image = image.resize((550, 370))
        # self.weather_pic = ImageTk.PhotoImage(image)

    def set_weather_info(self):
        self.get_weather()
        self.set_weather_picture()
        self.weather_type_label.setText(self._translate(
            "MainWindow",
            "<html><head/><body><p><span style=\"font-size:10pt; font-weight:600; color:#ffffff;\" "
            f">Погода: {self.weather['description']}</span></p></body></html>"))
        self.temperature_label.setText(self._translate(
            "MainWindow",
            f"<html><head/><body><p><span style=\" font-size:8pt; font-weight:550; "
            f"color:#ffffff;\">Температура: {self.weather['temp']}°C</span></p></body></html>"))
        self.humidity_label.setText(self._translate(
            "MainWindow",
            "<html><head/><body><p><span style=\" font-size:8pt; font-weight:550; color:#ffffff;\">Вологість: "
            f"{self.weather['humidity']}%</span></p></body></html>"))
        self.wind_label.setText(self._translate(
            "MainWindow",
            "<html><head/><body><p><span style=\" font-size:13pt; "
            f"font-weight:600; color:#ffffff;\">{self.weather['wind_speed']} м/с</span></p></body></html>"))

    def set_clock_info(self, current_datetime: dt.datetime):
        time_now = current_datetime.strftime(self.time_format)
        self.time_label.setText(self._translate(
            "MainWindow",
            "<html><head/><body><p><span style=\" font-size:12pt; font-weight:550; color:#00007f;\">"
            f"{time_now}</span></p></body></html>"))

    def set_calendar_info(self, current_datetime: dt.datetime):
        date_now = current_datetime.strftime(self.date_format)
        self.date_label.setText(self._translate(
            "MainWindow",
            f"<html><body><p><span style=\" font-size:10pt; color:#00007f;\">{date_now}</span></p></body></html>"))

    def info_update(self):
        self.set_geo_info()
        self.set_weather_info()
        cycle_count = 0
        weather_cycle = 1799
        while not self.update_process_stop:
            dt_now = dt.datetime.now()
            self.set_clock_info(dt_now)
            self.scheduler.exec_jobs()
            if cycle_count % 60 == 0:
                self.set_calendar_info(dt_now)
            elif cycle_count % weather_cycle == 0:
                try:
                    self.set_weather_info()
                    weather_cycle = 1799
                except ConnectionError:
                    weather_cycle = 31
            elif cycle_count != 0 and cycle_count % 3599 == 0:
                self.set_geo_info()
                cycle_count = -1
            time.sleep(0.5)
            cycle_count += 1

    def run_info_update_tread(self):
        self.update_process = threading.Thread(target=self.info_update)  # Создаем процесс для обновления данных
        self.update_process.setDaemon(True)
        self.update_process.start()  # Запускаем процесс

    def exit_app(self):
        self.dialog_process_stop = True
        self.update_process_stop = True
        time.sleep(1)
        self.main_window.close()
        sys.exit()


if __name__ == "__main__":
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)
    app = QtWidgets.QApplication(sys.argv)
    ui = AppUI()
    main_window = QtWidgets.QMainWindow()
    ui.setupUi(main_window)
    main_window.show()
    sys.exit(app.exec_())
