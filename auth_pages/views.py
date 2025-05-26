from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .models import PasswordResetToken
import uuid
from django.utils import timezone
from datetime import timedelta

def registration_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует')
            return render(request, 'auth_pages/registration.html')

        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            user.save()
            login(request, user)
            next_url = request.session.pop('next', 'profiles:profile')
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect(next_url)
        except Exception as e:
            messages.error(request, 'Ошибка при регистрации. Попробуйте снова.')
            return render(request, 'auth_pages/registration.html')

    return render(request, 'auth_pages/registration.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)

            if user is not None:
                login(request, user)
                next_url = request.session.pop('next', 'profiles:profile')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверный email или пароль')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь с таким email не найден')

    return render(request, 'auth_pages/login.html')

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
            token = str(uuid.uuid4())

            PasswordResetToken.objects.create(
                user=user,
                token=token,
                expires_at=timezone.now() + timedelta(hours=1)
            )

            reset_link = request.build_absolute_uri(
                reverse('auth_pages:reset_password', kwargs={'token': token})
            )

            send_mail(
                'Сброс пароля Ruta',
                f'Перейдите по ссылке для сброса пароля: {reset_link}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            messages.success(request, 'Ссылка для сброса пароля отправлена на ваш email')
            return redirect('auth_pages:login')

        except User.DoesNotExist:
            messages.error(request, 'Пользователь с таким email не найден')
        except Exception as e:
            messages.error(request, 'Ошибка при отправке письма. Попробуйте снова.')

    return render(request, 'auth_pages/forgot_password.html')

def reset_password_view(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token)

        if not reset_token.is_valid():
            messages.error(request, 'Ссылка истекла или недействительна')
            return redirect('auth_pages:forgot_password')

        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password != confirm_password:
                messages.error(request, 'Пароли не совпадают')
                return render(request, 'auth_pages/reset_password.html')

            if len(password) < 8:
                messages.error(request, 'Пароль должен содержать минимум 8 символов')
                return render(request, 'auth_pages/reset_password.html')

            reset_token.user.set_password(password)
            reset_token.user.save()
            reset_token.delete()

            messages.success(request, 'Пароль успешно изменен')
            return redirect('auth_pages:login')

    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Недействительная ссылка для сброса пароля')
        return redirect('auth_pages:forgot_password')

    return render(request, 'auth_pages/reset_password.html')