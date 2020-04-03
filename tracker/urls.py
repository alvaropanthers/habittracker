from django.urls import path
from . import views

app_name = "tracker"
urlpatterns = [
    path('api/templates', views.get_templates, name="getTemplates"),
    path('api/templates/<int:month>', views.get_templates_by_month, name="getTemplatesByMonth"),
    path('api/template/<int:habit_id>', views.get_template_by_habit_id, name="getTemplateByHabitId"),
    path('api/template/<int:habit_id>/<int:month>', views.get_template_by_habit_id_and_month, name='GetTemplateByHabitIdAndMonth'),
    # path('api/template', views.save_template, name="saveTemplate")

    #make an entity called template that represents a habit and its checked days
]


#api/templates <- Gives the templates of current month
#api/templates/<int:month> <- Gives the templates of specified month
#api/template/<int:habit_id> <- Gives the template of specified habit
#api/template/<int:habit_id>/<int:month> <- Gives the template of specified habit and month