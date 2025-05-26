# profiles/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.models import User
from blog.models import Post
from trips.models import Trip  # Добавляем импорт модели Trip
from .forms import UserProfileForm
from .models import UserProfile

@login_required
def profile_view(request):
    user = request.user
    posts = Post.objects.filter(user=user, slug__isnull=False).exclude(slug='').order_by('-created_at')
    planned_trips = user.trips.filter(status='planned', slug__isnull=False).exclude(slug='').order_by('-created_at')
    completed_trips = user.trips.filter(status='completed', slug__isnull=False).exclude(slug='').order_by('-created_at')

    context = {
        'user': user,
        'posts': posts,
        'planned_trips': planned_trips,
        'completed_trips': completed_trips,
        'stats': {
            'planned_trips_count': planned_trips.count(),
            'completed_trips_count': completed_trips.count(),
            'posts_count': posts.count(),
        }
    }
    return render(request, 'profiles/profile.html', context)

@login_required
def edit_profile_view(request):
    user = request.user
    try:
        user_profile = user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile, initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        })
        if form.is_valid():
            # Обновляем данные пользователя
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            # Сохраняем профиль
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profiles:profile')
        else:
            messages.error(request, 'Ошибка при обновлении профиля. Проверьте данные.')
    else:
        form = UserProfileForm(instance=user_profile, initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        })

    return render(request, 'profiles/edit_profile.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')