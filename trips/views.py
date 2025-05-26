from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Trip, TripPoint
from django.utils import timezone
import os
from django.conf import settings
import uuid

def popular_routes(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Пожалуйста, зарегистрируйтесь, чтобы просмотреть популярные маршруты.')
        request.session['next'] = request.get_full_path()
        return redirect('auth_pages:registration')

    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    trips = Trip.objects.all().order_by('-created_at')
    if query:
        trips = trips.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if status_filter:
        trips = trips.filter(status=status_filter)

    trips_data = []
    for trip in trips:
        trip_dict = {
            'title': trip.title,
            'description': trip.description,
            'image': trip.image,
            'date': trip.date,
            'status': trip.get_status_display(),
            'slug': trip.slug,
            'tags': [tag.strip() for tag in trip.tags.split(',')] if trip.tags else []
        }
        trips_data.append(trip_dict)

    return render(request, 'trips/popular_routes.html', {'trips': trips_data, 'query': query, 'status': status_filter})

@login_required
def add_trip_view(request):
    form_data = request.session.get('trip_form_data', {})
    points = request.session.get('trip_points', [])
    step = int(request.POST.get('step', 1)) if request.method == 'POST' else 1

    def save_temp_file(uploaded_file):
        if not uploaded_file:
            return None
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        file_name = f"{uuid.uuid4()}_{uploaded_file.name}"
        temp_path = os.path.join(temp_dir, file_name)
        with open(temp_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        return os.path.join('temp', file_name)

    if request.method == 'POST':
        if step == 1:
            form_data = {
                'title': request.POST.get('title', ''),
                'description': request.POST.get('description', ''),
                'tags': request.POST.get('tags', ''),
                'image_path': save_temp_file(request.FILES.get('image')),
            }
            request.session['trip_form_data'] = form_data
            step = 2

        elif step == 2:
            if 'add_point' in request.POST:
                point = {
                    'name': request.POST.get('point_name', ''),
                    'point_type': request.POST.get('point_type', 'intermediate'),
                    'address': request.POST.get('address', ''),
                    'description': request.POST.get('point_description', ''),
                    'lat': request.POST.get('lat', ''),
                    'lng': request.POST.get('lng', ''),
                    'image_path': save_temp_file(request.FILES.get('point_image')),
                }
                points.append(point)
                request.session['trip_points'] = points
            elif 'delete_point' in request.POST:
                index = int(request.POST.get('delete_point'))
                if 0 <= index < len(points):
                    if points[index].get('image_path'):
                        temp_file = os.path.join(settings.MEDIA_ROOT, points[index]['image_path'])
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                    points.pop(index)
                    request.session['trip_points'] = points
            elif 'next_step' in request.POST:
                step = 3

        elif step == 3 and 'save' in request.POST:
            try:
                status = request.POST.get('status', 'planned')
                trip = Trip.objects.create(
                    user=request.user,
                    title=form_data.get('title', ''),
                    description=form_data.get('description', ''),
                    tags=form_data.get('tags', ''),
                    date=request.POST.get('date', None) or timezone.now().date(),
                    status=status,
                    created_at=timezone.now(),
                )
                if form_data.get('image_path'):
                    temp_path = os.path.join(settings.MEDIA_ROOT, form_data['image_path'])
                    if os.path.exists(temp_path):
                        with open(temp_path, 'rb') as f:
                            trip.image.save(os.path.basename(form_data['image_path']), f)
                        os.remove(temp_path)

                for point_data in points:
                    point = TripPoint.objects.create(
                        trip=trip,
                        name=point_data['name'],
                        point_type=point_data['point_type'],
                        address=point_data['address'],
                        description=point_data['description'],
                        latitude=float(point_data['lat']) if point_data['lat'] else None,
                        longitude=float(point_data['lng']) if point_data['lng'] else None,
                    )
                    if point_data.get('image_path'):
                        temp_path = os.path.join(settings.MEDIA_ROOT, point_data['image_path'])
                        if os.path.exists(temp_path):
                            with open(temp_path, 'rb') as f:
                                point.image.save(os.path.basename(point_data['image_path']), f)
                            os.remove(temp_path)

                request.session.pop('trip_form_data', None)
                request.session.pop('trip_points', None)
                messages.success(request, 'Маршрут успешно создан!')
                return redirect('profiles:profile')

            except Exception as e:
                messages.error(request, f'Ошибка при сохранении маршрута: {str(e)}')
                step = 3

        request.session['trip_form_data'] = form_data
        request.session['trip_points'] = points
        request.session.modified = True

    return render(request, 'trips/add_trip.html', {
        'step': step,
        'form_data': form_data,
        'points': points,
    })

def trip_detail(request, slug):
    if not request.user.is_authenticated:
        messages.info(request, 'Пожалуйста, зарегистрируйтесь, чтобы просмотреть детали маршрута.')
        request.session['next'] = request.get_full_path()
        return redirect('auth_pages:registration')

    trip = get_object_or_404(Trip, slug=slug)
    points = trip.points.all()
    tags = [tag.strip() for tag in trip.tags.split(',')] if trip.tags else []
    return render(request, 'trips/trip_detail.html', {
        'trip': trip,
        'points': points,
        'tags': tags,
    })

@login_required
def edit_trip_view(request, slug):
    trip = get_object_or_404(Trip, slug=slug)
    if request.user != trip.user:
        messages.error(request, 'Вы не можете редактировать этот маршрут.')
        return redirect('trips:trip_detail', slug=slug)

    form_data = request.session.get('trip_form_data', {
        'title': trip.title,
        'description': trip.description,
        'tags': trip.tags,
        'date': trip.date,
        'status': trip.status,
        'image_path': trip.image.url if trip.image else None,
    })
    points = request.session.get('trip_points', [
        {
            'id': point.id,
            'name': point.name,
            'point_type': point.point_type,
            'address': point.address,
            'description': point.description,
            'lat': str(point.latitude) if point.latitude else '',
            'lng': str(point.longitude) if point.longitude else '',
            'image_path': point.image.url if point.image else None,
        } for point in trip.points.all()
    ])
    step = int(request.POST.get('step', 1)) if request.method == 'POST' else 1

    def save_temp_file(uploaded_file):
        if not uploaded_file:
            return None
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        file_name = f"{uuid.uuid4()}_{uploaded_file.name}"
        temp_path = os.path.join(temp_dir, file_name)
        with open(temp_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        return os.path.join('temp', file_name)

    if request.method == 'POST':
        if step == 1:
            form_data = {
                'title': request.POST.get('title', ''),
                'description': request.POST.get('description', ''),
                'tags': request.POST.get('tags', ''),
                'image_path': save_temp_file(request.FILES.get('image')) or form_data.get('image_path'),
            }
            request.session['trip_form_data'] = form_data
            step = 2

        elif step == 2:
            if 'add_point' in request.POST:
                point = {
                    'id': None,
                    'name': request.POST.get('point_name', ''),
                    'point_type': request.POST.get('point_type', 'intermediate'),
                    'address': request.POST.get('address', ''),
                    'description': request.POST.get('point_description', ''),
                    'lat': request.POST.get('lat', ''),
                    'lng': request.POST.get('lng', ''),
                    'image_path': save_temp_file(request.FILES.get('point_image')),
                }
                points.append(point)
                request.session['trip_points'] = points
            elif 'delete_point' in request.POST:
                point_id = request.POST.get('delete_point')
                points[:] = [p for p in points if str(p.get('id')) != point_id]
                TripPoint.objects.filter(id=point_id).delete()
                request.session['trip_points'] = points
            elif 'next_step' in request.POST:
                step = 3

        elif step == 3 and 'save' in request.POST:
            try:
                trip.title = form_data.get('title', '')
                trip.description = form_data.get('description', '')
                trip.tags = form_data.get('tags', '')
                trip.date = request.POST.get('date', trip.date)
                trip.status = request.POST.get('status', 'planned')
                if form_data.get('image_path') and not form_data['image_path'].startswith('/media/trips/'):
                    temp_path = os.path.join(settings.MEDIA_ROOT, form_data['image_path'])
                    if os.path.exists(temp_path):
                        with open(temp_path, 'rb') as f:
                            trip.image.save(os.path.basename(form_data['image_path']), f)
                        os.remove(temp_path)
                trip.save()

                # Обновляем точки
                existing_point_ids = {p.get('id') for p in points if p.get('id')}
                trip.points.exclude(id__in=existing_point_ids).delete()
                for point_data in points:
                    if point_data.get('id'):
                        point = TripPoint.objects.get(id=point_data['id'])
                        point.name = point_data['name']
                        point.point_type = point_data['point_type']
                        point.address = point_data['address']
                        point.description = point_data['description']
                        point.latitude = float(point_data['lat']) if point_data['lat'] else None
                        point.longitude = float(point_data['lng']) if point_data['lng'] else None
                        if point_data.get('image_path') and not point_data['image_path'].startswith('/media/trip_points/'):
                            temp_path = os.path.join(settings.MEDIA_ROOT, point_data['image_path'])
                            if os.path.exists(temp_path):
                                with open(temp_path, 'rb') as f:
                                    point.image.save(os.path.basename(point_data['image_path']), f)
                                os.remove(temp_path)
                        point.save()
                    else:
                        point = TripPoint.objects.create(
                            trip=trip,
                            name=point_data['name'],
                            point_type=point_data['point_type'],
                            address=point_data['address'],
                            description=point_data['description'],
                            latitude=float(point_data['lat']) if point_data['lat'] else None,
                            longitude=float(point_data['lng']) if point_data['lng'] else None,
                        )
                        if point_data.get('image_path'):
                            temp_path = os.path.join(settings.MEDIA_ROOT, point_data['image_path'])
                            if os.path.exists(temp_path):
                                with open(temp_path, 'rb') as f:
                                    point.image.save(os.path.basename(point_data['image_path']), f)
                                os.remove(temp_path)

                request.session.pop('trip_form_data', None)
                request.session.pop('trip_points', None)
                messages.success(request, 'Маршрут успешно обновлен!')
                return redirect('trips:trip_detail', slug=trip.slug)

            except Exception as e:
                messages.error(request, f'Ошибка при сохранении маршрута: {str(e)}')
                step = 3

        request.session['trip_form_data'] = form_data
        request.session['trip_points'] = points
        request.session.modified = True

    return render(request, 'trips/edit_trip.html', {
        'trip': trip,
        'step': step,
        'form_data': form_data,
        'points': points,
    })

@login_required
def delete_trip_view(request, slug):
    trip = get_object_or_404(Trip, slug=slug)
    if request.user != trip.user:
        messages.error(request, 'Вы не можете удалить этот маршрут.')
        return redirect('trips:trip_detail', slug=slug)
    trip.delete()
    messages.success(request, 'Маршрут успешно удален!')
    return redirect('profiles:profile')