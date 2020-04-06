from django.utils import timezone

_MIN_YEAR = 2000

def break_formatted_date(date):
    try:
        items = list(map(int, date.split('-')))
        if len(items) == 3 and is_month(items[0]) and is_day(items[1]) and is_year(items[2]):
            return items
    except ValueError:
        pass

    return []

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
    try:
        val = int(value)
    except ValueError:
        return False

    return True

LOG_DEFAULT = 0
LOG_ERROR = 1
def log(string, type=LOG_DEFAULT):
    with open('tracker/logs/log.log', 'a') as file:
        dt = timezone.now()
        if type == LOG_DEFAULT:
            file.write('DEFAULT LOG\n')
        elif type == LOG_ERROR:
            file.write('ERROR LOG\n')

        file.write(f'{format_date(dt.month, dt.day, dt.year)} ---- {dt.hour}:{dt.minute}:{dt.second}:{dt.microsecond}\n')
        file.write(f'{str(string)}\n')
        file.write(100 * '-')
        file.write('\n')

