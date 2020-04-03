from django.contrib import admin
from .models import Habit, CheckedDay

admin.site.register(Habit)
admin.site.register(CheckedDay)
