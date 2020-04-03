from django.utils import timezone

def break_formatted_date(date):
    return list(map(int, date.split('-')))

def format_date(month, day, year):
    return f"{month}-{day}-{year}"

def is_month(month):
    return is_integer(month) and 1 <= month <= 12

def is_day(day):
    return is_integer(month) and 1 <= month <= 31

def is_year(year):
    return is_integer(year) and 2000 <= year <= timezone.now().year

def is_date(date):
    items = break_formatted_date(date)
    return len(date) == 3 and is_month(items[0]) and is_day(items[1]) and is_year(items[2])

def is_integer(value):
    return type(value) == int