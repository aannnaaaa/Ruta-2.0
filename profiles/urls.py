from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('', views.profile_view, name='profile'),
    path('edit/', views.edit_profile_view, name='edit_profile'),
    path('logout/', views.logout_view, name='logout'),
]