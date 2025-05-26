from django.urls import path
from . import views

app_name = 'trips'

urlpatterns = [
    path('popular/', views.popular_routes, name='popular_routes'),
    path('add/', views.add_trip_view, name='add_trip'),
    path('trip/<str:slug>/', views.trip_detail, name='trip_detail'),
    path('trip/<str:slug>/edit/', views.edit_trip_view, name='edit_trip'),
    path('trip/<str:slug>/delete/', views.delete_trip_view, name='delete_trip'),
]