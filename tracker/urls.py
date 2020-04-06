from django.urls import path
from . import views

app_name = "tracker"
urlpatterns = [
    path('api/templates', views.get_templates, name="getTemplates"),
    path('api/templates/<int:month>', views.get_templates_by_month, name="getTemplatesByMonth"),
    path('api/template/<int:habit_id>', views.get_template_by_habit_id, name="getTemplateByHabitId"),
    path('api/template/<int:habit_id>/<int:month>', views.get_template_by_habit_id_and_month, name='getTemplateByHabitIdAndMonth'),
    path('api/habit', views.create_habit_resource, name='createHabitResource'),
    path('api/template', views.create_template_resource, name='createTemplateResource'),
]