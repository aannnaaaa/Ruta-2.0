from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post
from .forms import PostForm

def blog_page(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Пожалуйста, зарегистрируйтесь, чтобы просмотреть блог.')
        request.session['next'] = request.get_full_path()
        return redirect('auth_pages:registration')

    posts = Post.objects.all().order_by('-created_at')
    posts_data = []
    for post in posts:
        post_dict = {
            'id': post.id,
            'title': post.title,
            'description': post.description,
            'image': post.image,
            'created_at': post.created_at,
            'user': post.user,
            'views': post.views,
            'slug': post.slug,
            'tags': [tag.strip() for tag in post.tags.split(',')] if post.tags else []
        }
        posts_data.append(post_dict)

    return render(request, 'blog/blog_page.html', {'posts': posts_data})

def post_detail(request, slug):
    if not request.user.is_authenticated:
        messages.info(request, 'Пожалуйста, зарегистрируйтесь, чтобы просмотреть детали поста.')
        request.session['next'] = request.get_full_path()
        return redirect('auth_pages:registration')

    post = get_object_or_404(Post, slug=slug)
    post.views += 1
    post.save()
    tags = [tag.strip() for tag in post.tags.split(',')] if post.tags else []
    return render(request, 'blog/post_detail.html', {'post': post, 'tags': tags})

@login_required
def add_post_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Пост успешно опубликован!')
            return redirect('profiles:profile')
        else:
            messages.error(request, 'Ошибка при создании поста. Проверьте данные.')
    else:
        form = PostForm()
    return render(request, 'blog/add_post.html', {'form': form})

@login_required
def edit_post_view(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.user != post.user:
        messages.error(request, 'Вы не можете редактировать этот пост.')
        return redirect('blog:post_detail', slug=slug)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пост успешно обновлен!')
            return redirect('blog:post_detail', slug=post.slug)
        else:
            messages.error(request, 'Ошибка при редактировании поста. Проверьте данные.')
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post_view(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.user != post.user:
        messages.error(request, 'Вы не можете удалить этот пост.')
        return redirect('blog:post_detail', slug=slug)
    post.delete()
    messages.success(request, 'Пост успешно удален!')
    return redirect('profiles:profile')