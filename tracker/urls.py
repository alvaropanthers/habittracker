from django.urls import path
from . import views

app_name = "tracker"
urlpatterns = [
    path('api/template', views.TemplateView.as_view()),
    path('api/templates', views.TemplatesView.as_view())
]