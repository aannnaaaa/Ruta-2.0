from django.urls import path
from . import views

app_name = 'about_page'

urlpatterns = [
    path('', views.about_view, name='about'),
]