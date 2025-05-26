from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from about_page.views import about_view  # Импортируем about_view

urlpatterns = [
    path('', about_view, name='home'),  # Добавляем корневой маршрут
    path('admin/', admin.site.urls),
    path('auth/', include('auth_pages.urls')),
    path('profile/', include('profiles.urls')),
    path('blog/', include('blog.urls')),
    path('about/', include('about_page.urls')),
    path('routes/', include('trips.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)