from django.shortcuts import render
from trips.models import Trip
from blog.models import Post

def about_view(request):
    trips = Trip.objects.all().order_by('-created_at')[:3]
    posts = Post.objects.filter(slug__isnull=False).exclude(slug='').order_by('-created_at')[:3]
    context = {
        'trips': trips,
        'posts': posts,
    }
    return render(request, 'about_page/about.html', context)

def routes_view(request):
    return render(request, 'about_page/routes.html')