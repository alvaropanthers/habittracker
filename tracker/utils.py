from django.utils import timezone

_MIN_YEAR = 2000

def break_formatted_date(date):
    items = list(map(int, date.split('-')))
    return items if len(items) == 3 else []

def format_date(month, day, year): #value error if a string is passed
    month = int(month)
    day = int(day)
    year = int(year)

    if  0 < month < 10:
        month = f'0{month}'
    elif month == 0:
        month = '01' 
    
    if 0 < day < 10:
        day = f'0{day}'
    elif day == 0:
        day = '01'

    if not (1995 <= year <= 2020):
        raise ValueError

    return f"{month}-{day}-{year}"

def is_month(month):
    try:
        return 1 <= int(month) <= 12
    except ValueError:
        return False

def is_day(day):
    try:
        return 1 <= int(day) <= 31
    except ValueError:
        return False

def is_year(year):
    try:
        return _MIN_YEAR <= int(year) <= timezone.now().year
    except ValueError:
        return False

def is_date(date):
    try:
        month, day, year = break_formatted_date(date)
        return is_month(month) and is_day(day) and is_year(year)
    except ValueError:
        return False

def is_integer(value):
    return type(value) == int