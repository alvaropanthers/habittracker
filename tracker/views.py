from django.shortcuts import render
from django.http.response import HttpResponse, JsonResponse
from django.http.request import HttpRequest
from django.utils import timezone
from datetime import datetime
from .models import Habit, CheckedDay
from . import utils

#Return all templates
def get_templates(request):
    return JsonResponse(get_all_templates())

#Return all templates of specified month
def get_templates_by_month(request, month):
    return JsonResponse(get_all_templates(month))

#Returns the template of specified habit
def get_template_by_habit_id(request, habit_id):
    return JsonResponse(get_template(habit_id=habit_id))

#Returns the template of specified habit and month
def get_template_by_habit_id_and_month(request, habit_id, month):
    return JsonResponse(get_template(habit_id, month))

#return list of habits with corresponding completed days given the month
#Need to use timezone instead of datetime, read about timezone below
#https://docs.djangoproject.com/en/3.0/topics/i18n/timezones/
#Is good practice to store datetime data in UTC. The main reason is Daylight Saving Time.
def get_all_templates(month=timezone.now().month):
    items = {}
    if 1 <= month <= 31:
        habits = Habit.objects.all()
        for habit in habits:
            items[habit.id] = {'id': habit.id, 'name': habit.name, 'checkeddays': {}}
            for index, day in enumerate(habit.checkedday_set.filter(date__month=month)):
                items[habit.id]['checkeddays'][index] = {'date': f"{utils.format_date(day.date.month, day.date.day, day.date.year)}"}            

    return items

def get_template(habit_id, month=timezone.now().month):
    items = {}
    try:
        habit = Habit.objects.get(pk=habit_id)
        items[habit.id] = {'id': habit.id, 'name': habit.name, 'checkedday':{}}
        for index, day in enumerate(habit.checkedday_set.filter(date__month=month)):
            items[habit.id]['checkedday'][index] = {'date': f"{utils.format_date(day.date.month, day.date.day, day.date.year)}"}
    except Habit.DoesNotExist:
        pass
    
    return items

def save_template(request):
    if request.method == 'POST' and len(request.POST) > 0:
        habit_id = request.POST['habit_id']
        checkeddays = [utils.break_formatted_date(request.POST[f'day{index}']) for index in range(1, 32) if f'day{index}' in request.POST and utils.is_date(f'day{index}')]

        if utils.is_integer(habit_id) and not (not checkeddays):
            try:
                habit = Habit.objects.get(pk=habit_id)
                for date in checkeddays:
                    d = CheckedDay(habit=habit, date=timezone.now().replace(month=date[0], day=date[1], year=date[2]))
                    d.save()
                
                return HttpResponse('Items were modified 201')
            except Habit.DoesNotExist:
                return HttpResponse("Item does not exists") #CORRECT THIS TO APPROPRIATE RESPONSE

        return HttpResponse('Nothing to save... nothing was modified')

    return HttpResponse("MUST BE A POST REQUEST")
