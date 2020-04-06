from django.shortcuts import render
from django.http.response import HttpResponse, JsonResponse
from django.http.request import HttpRequest
from django.utils import timezone
from datetime import datetime
from .models import Habit, CheckedDay
from . import utils
from . import status

def prepare_resource(data, msg=status.HTTP_404_MESSAGE, status=status.HTTP_404_NOT_FOUND):
    if not data:
        return HttpResponse(msg, status=status)

    return JsonResponse(data)

#Return all templates
def get_templates(request):
    return prepare_resource(get_all_templates())

#Return all templates of specified month
def get_templates_by_month(request, month):
    return prepare_resource(get_all_templates(month))

#Returns the template of specified habit
def get_template_by_habit_id(request, habit_id):
    return prepare_resource(get_template(habit_id=habit_id))

#Returns the template of specified habit and month
def get_template_by_habit_id_and_month(request, habit_id, month):
    return prepare_resource(get_template(habit_id, month))

def create_habit_resource(request):
    item = {}
    if request.method == 'POST':
        habit_name = request.POST['name'] if 'name' in request.POST else None
        data = save_habit(habit_name)
        if data:
            item = data
        else:
            return prepare_resource(None, msg='name min len is 5', status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    return prepare_resource(item)

def create_template_resource(request):
    items = {}
    if request.method == 'POST':
        habit_id = request.POST['habit_id'] if 'habit_id' in request.POST else None
        checkeddays = [request.POST[f'day{index}'] for index in range(1, 32) if f'day{index}' in request.POST]
        if habit_id and checkeddays:
            try:
                items = save_template(habit_id, checkeddays)
            except ValueError:
                return prepare_resource(None, msg='Malformed paremeter values', status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        else:
            return prepare_resource(None, msg='Missing parameters', status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    return prepare_resource(items)

#return list of habits with corresponding completed days given the month
#Need to use timezone instead of datetime, read about timezone below
#https://docs.djangoproject.com/en/3.0/topics/i18n/timezones/
#Is good practice to store datetime data in UTC. The main reason is Daylight Saving Time.
#Returns {} if nothing is found or parameters are incorrect
def get_all_templates(month=None, year=None):
    now = timezone.now()
    month = month if month is not None else now.month
    year = year if year is not None else now.year
    items = {}

    if utils.is_month(month) and utils.is_year(year):
        habits = Habit.objects.all()
        for index, habit in enumerate(habits):
            days = habit.checkedday_set.filter(date__month=month, date__year=year)
            items[index] = create_template(habit, days)

    return items

def get_template(habit_id, month=None, year=None):
    now = timezone.now()
    month = month if month is not None else now.month
    year = year if year is not None else now.year
    item = {}

    if utils.is_month(month) and utils.is_year(year):
        try:
            habit = Habit.objects.get(pk=habit_id)
            days = habit.checkedday_set.filter(date__month=month, date__year=year)
            item = create_template(habit, days)
        except Habit.DoesNotExist:
            pass

    return item

def create_template(habit, checkeddays):
    return {
        'id': habit.id, 
        'name': habit.name, 
        'checkeddays': { i: f"{utils.format_date(day.date.month, day.date.day, day.date.year)}" for i, day in enumerate(checkeddays)}
        }

MIN_LEN_HABIT_NAME = 5
def save_habit(name):
    if name and len(name) >= MIN_LEN_HABIT_NAME:
        habit = Habit(name=name)
        habit.save()
        return create_template(habit, {})

    return False


def save_template(habit_id, dates):
    fdates = [utils.break_formatted_date(date) for date in dates if type(date) == str]

    if utils.is_integer(habit_id) and not ([] in fdates):
        try:
            habit = Habit.objects.get(pk=habit_id)
            checkeddays = []
            for date in fdates:
                month, day, year = date
                d = CheckedDay(habit=habit, date=timezone.now().replace(month=month, day=day, year=year))
                d.save()
                checkeddays.append(d)

            return create_template(habit, checkeddays)
        except Habit.DoesNotExist:
            return False
    
    raise ValueError