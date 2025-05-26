# trips/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

class Trip(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Запланировано'),
        ('completed', 'Посещено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips', verbose_name='Автор')
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание', blank=True)
    image = models.ImageField(upload_to='trips/', blank=True, null=True, verbose_name='Изображение')
    date = models.DateField(verbose_name='Дата')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned', verbose_name='Статус')
    slug = models.SlugField(max_length=250, unique=True, blank=True, verbose_name='URL')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    tags = models.CharField(max_length=200, blank=True, verbose_name='Теги')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{uuid.uuid4()}")[:250]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Маршрут'
        verbose_name_plural = 'Маршруты'

class TripPoint(models.Model):
    POINT_TYPES = [
        ('start', 'Начало'),
        ('intermediate', 'Промежуточная точка'),
        ('end', 'Конец'),
    ]

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='points', verbose_name='Маршрут')
    name = models.CharField(max_length=200, verbose_name='Название точки')
    point_type = models.CharField(max_length=20, choices=POINT_TYPES, default='intermediate', verbose_name='Тип точки')
    address = models.CharField(max_length=300, blank=True, verbose_name='Адрес')
    description = models.TextField(blank=True, verbose_name='Описание')
    latitude = models.FloatField(blank=True, null=True, verbose_name='Широта')
    longitude = models.FloatField(blank=True, null=True, verbose_name='Долгота')
    image = models.ImageField(upload_to='trip_points/', blank=True, null=True, verbose_name='Изображение')

    def __str__(self):
        return f"{self.name} ({self.get_point_type_display()})"

    class Meta:
        verbose_name = 'Точка маршрута'
        verbose_name_plural = 'Точки маршрутов'