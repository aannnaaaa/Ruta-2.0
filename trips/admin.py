from django.contrib import admin
from .models import Trip, TripPoint

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'date', 'is_completed', 'is_public']
    list_filter = ['is_completed', 'is_public']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ['title']}
