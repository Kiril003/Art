import logging
import re
import datetime as dt

from ru_word2number import w2n


logger = logging.getLogger(__name__)

REVERTED_DAY_OF_WEEK = {'понеділок': 1, 'вівторок': 2, 'середу': 3, 'четвер': 4,
                        "п'ятницю": 5, 'суботу': 6, 'неділю': 7}


def define_reminder_day(now: dt.datetime, day_kw: str = None) -> int:
    now_weekday = now.isoweekday()
    day = now.day
    if day_kw:
        if day_kw == 'сьогодні':
            day = now.day
        elif day_kw == 'завтра':
            day = now.day + 1
        elif day_kw == 'післязавтра':
            day = now.day + 2
        else:
            weekday = REVERTED_DAY_OF_WEEK[day_kw]
            delta = weekday - now_weekday
            if delta > 0:
                reminder_dt = now + dt.timedelta(days=delta)
            else:
                reminder_dt = now + dt.timedelta(days=7 + delta)
            day = reminder_dt.day
    return day


def define_reminder_hour(now: dt.datetime,
                         words: list[str],
                         hour_kw: str = None) -> int:
    if not hour_kw:
        return now.hour + 1
    hour_kw = hour_kw[0].strip()
    hours_word = words[words.index(hour_kw) - 1]
    return w2n.word_to_num(hours_word)


def define_reminder_minute(words: list[str], minute_kw: str = None) -> int:
    if not minute_kw:
        return 0
    minute_kw = minute_kw[0].strip()
    minutes_word = words[words.index(minute_kw) - 1]
    return w2n.word_to_num(minutes_word)


def define_time_cherez(now: dt.datetime,
                       words: list[str],
                       day_kw: str,
                       hour_kw: str,
                       minute_kw: str,
                       cherez_kw: str):
    try:
        interval_word = words[words.index(cherez_kw) + 1]
        interval = w2n.word_to_num(interval_word)
    except ValueError:
        logger.error(f"Can't find numeric word in words:\n{words}")
        err = "Не вдається знайти числове слово в рядку:\n{words}"
        return None, None, None, err
    else:
        if day_kw:
            return now.day + interval, now.hour, now.minute, None
        elif hour_kw:
            set_time = now + dt.timedelta(hours=interval)
            return set_time.day, set_time.hour, set_time.minute, None
        else:
            set_time = now + dt.timedelta(minutes=interval)
            return set_time.day, set_time.hour, set_time.minute, None


def get_reminder_settings(text: str):
    err = None
    logger.info(f'Getting datetime and text from voice reminder:\n{text}')
    words = text.split()
    now_datetime = dt.datetime.now()
    day_pattern = re.compile(
        r'сьогодні|післязавтра|завтра|понеділок|вівторок|середу|четвер|п\'ятницю|суботу|неділю'
    )
    day_kw = re.findall(day_pattern, text)
    hour_kw = re.findall(' годин| години| година| годині', text)
    minute_kw = re.findall(' хвилини| хвилину| хвилин', text)
    cherez_kw = re.findall('через', text)
    if cherez_kw:
        reminder_text = text.split(' через ')[0]
        day, hour, minute, err = define_time_cherez(now_datetime, words, day_kw, hour_kw, minute_kw, cherez_kw[0])
    else:
        if day_kw:
            day_kw = day_kw[0].strip()
            if day_kw in ['сьогодні', 'післязавтра', 'завтра']:
                reminder_text = text.split(f' {day_kw} ')[0]
            elif' во ' in text:
                reminder_text = text.split(' во ')[0]
            else:
                reminder_text = text.split(' в ')[0]
        elif not hour_kw and not minute_kw:
            reminder_text = text
        else:
            reminder_text = text.split(' в ')[0]
        day = define_reminder_day(now_datetime, day_kw)
        hour = define_reminder_hour(now_datetime, words, hour_kw)
        minute = define_reminder_minute(words, minute_kw)
    if err:
        return None, None, err
    return now_datetime.replace(day=day, hour=hour, minute=minute), reminder_text, None


if __name__ == '__main__':
    text = 'випити таблетку в п\'ятницю в десять годин'
    # reminder_dt, reminder_text = get_reminder_settings(text)
    print(*get_reminder_settings(text))

