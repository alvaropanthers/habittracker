from django.shortcuts import render
from django.http.response import HttpResponse, JsonResponse
from django.http.request import HttpRequest
from django.utils import timezone
from django.http import QueryDict
from datetime import datetime
from .models import Habit, CheckedDay
from . import utils
from . import status
from django.views import View
import json

class TemplateView(View):
    #Should use slug for template name instead
    def get(self, request):
        name = request.GET.get('name') if 'name' in request.GET else None 
        month = request.GET.get('month') if 'month' in request.GET else None
        year = request.GET.get('year') if 'year' in request.GET else None
        
        if name and month and year:
            template = Template(name=name, month=month, year=year)
            if not template.isNew():
                return JsonResponse(template.createTemplateDict())
        
        return HttpResponse('Invalid or missing data', status=status.HTTP_400_BAD_REQUEST)


    def post(self, request):
        name = request.POST_QD.get('name') if 'name' in request.POST_QD else None
        days = request.POST_QD.getlist('days') if 'days' in request.POST_QD else None
        month = request.POST_QD.get('month') if 'month' in request.POST_QD else None
        year = request.POST_QD.get('year') if 'year' in request.POST_QD else None

        if name and (len(name) >= MIN_LEN_HABIT_NAME) and not days:
            time = timezone.now()
            template = Template(name=name, month=time.month, year=time.year)
            if template.isNew():
                template.save()
                return JsonResponse(template.createTemplateDict())
            else:
                return HttpResponse('Resource already exists', status=status.HTTP_409_CONFLICT)
        elif name and days and month and year:
            template = Template(name=name, month=month, year=year)
            if not template.isNew():
                for day in days:
                    template.addDay(day)
                return JsonResponse(template.save())

        return HttpResponse('Invalid or missing data', status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        put = json.loads(request.body) #Might not work in production
        name = put['name'] if 'name' in put else None
        newName = put['newName'] if 'newName' in put else None
        # name = put.get('name') if 'name' in put else None
        # newName = put.get('newName') if 'newName' in put else None
        if name and newName:
            time = timezone.now()
            template = Template(name, month=time.month, year=time.year)
            if not template.isNew() and template.update(newName):
                template.save()
                return JsonResponse(template.createTemplateDict())

        return HttpResponse('Invalid or missing data', status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        name = request.DELETE_QD.get('name') if 'name' in request.DELETE_QD else None
        month = request.DELETE_QD.get('month') if 'month' in request.DELETE_QD else None
        year = request.DELETE_QD.get('year') if 'year' in request.DELETE_QD else None
        days = request.DELETE_QD.getlist('days') if 'days' in request.DELETE_QD else None

        if name and not days:
            time = timezone.now()
            template = Template(name, month=time.month, year=time.year)
            if not template.isNew() and template.delete():
                return HttpResponse('Deleted')
        elif name and month and year and days:
            template = Template(name, month=month, year=year)
            if not template.isNew():
                for day in days:
                    template.removeDay(day)
                return JsonResponse(template.save())

        return HttpResponse('Invalid or missing data', status=status.HTTP_400_BAD_REQUEST)

class TemplatesView(View):
    def get(self, request):
        month = request.GET.get('month') if 'month' in request.GET else None
        year = request.GET.get('year') if 'year' in request.GET else None
        
        month = request.GET_QD.get('month') if 'month' in request.GET_QD else None
        year = request.GET_QD.get('year') if 'year' in request.GET_QD else None

        if month and year:
            templates = Templates()
            result = templates.getAll(month=month, year=year)
            if result:
                return JsonResponse(result)

        return HttpResponse('Invalid or missing data', status=status.HTTP_400_BAD_REQUEST)

MIN_LEN_HABIT_NAME = 5
class Template:
    def __init__(self, name, month, year):
        try:
            self.habit = Habit.objects.get(name=name)
            self.new = False
        except Habit.DoesNotExist:
            self.habit = Habit(name=name)
            self.new = True
        
        self.month = month
        self.year = year
        self.days = []
        self.rmDays = []

    def addDay(self, day):
        try:
            self.rmDays.remove(day)
        except ValueError:
            pass
        
        self.days.append(day)
    
    def removeDay(self, day):
        try:
            self.days.remove(day)
        except ValueError:
            pass
        self.rmDays.append(day)

    def update(self, name):
        if name and (len(name) >= MIN_LEN_HABIT_NAME):
            self.habit.name = name
            return True
        
        return False

    def save(self):
        self.habit.save()
        
        #Save
        for day in self.days:
            try:
                self.habit.checkedday_set.get(date__month=self.month, date__year=self.year, date__day=day)
            except CheckedDay.DoesNotExist:
                newD = CheckedDay(habit=self.habit, date=timezone.now().replace(month=int(self.month), day=int(day), year=int(self.year)))
                newD.save()

        #Delete
        for day in self.rmDays:
            try:
                delD = self.habit.checkedday_set.get(date__month=self.month, date__year=self.year, date__day=day)
                delD.delete()
            except CheckedDay.DoesNotExist:
                pass
        
        return self.createTemplateDict()

    def delete(self):
        self.habit.delete()
        return True

    def isNew(self):
        return self.new

    def createTemplateDict(self):
        cds = self.habit.checkedday_set.filter(date__month=self.month, date__year=self.year)
        return { 'id': self.habit.id, 'name': self.habit.name, 'month': self.month, 'year': self.year, 'days': [ day.date.day for day in cds ] }

class Templates:
    #Need to use timezone instead of datetime, read about timezone below
    #https://docs.djangoproject.com/en/3.0/topics/i18n/timezones/
    #It's good practice to store datetime data in UTC. The main reason is Daylight Saving Time.
    def get(self, habit_id, month, year):
        item = {}
        if utils.is_month(month) and utils.is_year(year):
            try:
                habit = Habit.objects.get(pk=habit_id)
                days = habit.checkedday_set.filter(date__month=month, date__year=year)
                item = self.createTemplateDict(habit=habit, month=month, year=year, checkeddays=days)
            except Habit.DoesNotExist:
                pass

        return item

    def getAll(self, month, year):
        items = {}

        if utils.is_month(month) and utils.is_year(year):
            habits = Habit.objects.all()
            for index, habit in enumerate(habits):
                days = habit.checkedday_set.filter(date__month=month, date__year=year)
                items[index] = self.createTemplateDict(habit=habit, month=month, year=year, checkeddays=days)

        return items


    def resource(self, habit_id, month, year, days, create=True, delete=False):
        d = [int(day) if utils.is_day(day) else False for day in days]
        if utils.is_integer(habit_id) and utils.is_month(month) and utils.is_year(year) and not (False in d):
            try:
                habit = Habit.objects.get(pk=habit_id)
                for day in d:
                    try:
                        item = CheckedDay.objects.get(date__month=month, date__day=day, date__year=year)
                        if delete:
                            item.delete()
                    except CheckedDay.DoesNotExist:
                        if create:
                            newD = CheckedDay(habit=habit, date=timezone.now().replace(month=int(month), day=int(day), year=int(year)))
                            newD.save()
                if create or delete:
                    return self.createTemplateDict(habit, month, year, habit.checkedday_set.filter(date__month=month, date__year=year))
            except Habit.DoesNotExist:
                pass
        
        return False

    def add(self, habit_id, month, year, days):
        return self.resource(habit_id=habit_id, month=month, year=year, days=days)

    def delete(self, habit_id, month, year, days):
        return self.resource(habit_id=habit_id, month=month, year=year, days=days, create=False, delete=True)

    def createTemplateDict(self, habit, month, year, checkeddays):
        return { 'id': habit.id, 'name': habit.name, 'month': month, 'year': year, 'days': [ day.date.day for day in checkeddays ] }