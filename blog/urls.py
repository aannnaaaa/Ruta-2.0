from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
        path('', views.blog_page, name='blog'),
        path('post/<slug:slug>/', views.post_detail, name='post_detail'),
        path('add/', views.add_post_view, name='add_post'),
        path('post/<slug:slug>/edit/', views.edit_post_view, name='edit_post'),
        path('post/<slug:slug>/delete/', views.delete_post_view, name='delete_post'),
    ]