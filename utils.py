from datetime import date, timedelta


def today():
    return date.today().strftime("%d.%m.%Y")


def yesterday():
    return (date.today() - timedelta(days=1)).strftime("%d.%m.%Y")
