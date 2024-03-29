from datetime import datetime, timedelta
from config import TIME_REMARK


def full_today():
    return (datetime.now() + + timedelta(hours=TIME_REMARK)).strftime("%d.%m.%Y %H:%M:%S")


def today():
    return (datetime.now() + + timedelta(hours=TIME_REMARK)).strftime("%d.%m.%Y")


def yesterday():
    return (datetime.now() - timedelta(days=1) + timedelta(hours=TIME_REMARK)).strftime("%d.%m.%Y")
