from django.contrib import admin
from .models import Trip, TripPoint

class TripPointInline(admin.TabularInline):
    model = TripPoint
    extra = 1  # Количество пустых форм для добавления новых точек
    fields = ('name', 'point_type', 'address', 'description', 'latitude', 'longitude', 'image')

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'date', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'user')
    search_fields = ('title', 'description', 'tags')
    date_hierarchy = 'created_at'
    prepopulated_fields = {'slug': ('title',)}
    inlines = [TripPointInline]

@admin.register(TripPoint)
class TripPointAdmin(admin.ModelAdmin):
    list_display = ('name', 'trip', 'point_type', 'address', 'latitude', 'longitude')
    list_filter = ('point_type', 'trip')
    search_fields = ('name', 'address', 'description')