from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import Post, Category
from django.db.models import Q

def post_list(request):
    # Only show published posts (status=True)
    posts = Post.objects.filter(status=True)
    categories = Category.objects.all()

    # 1. Search Logic
    query = request.GET.get('q')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | 
            Q(body__icontains=query)
        )

    # 2. Category Filter Logic
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)

    context = {
        'posts': posts,
        'categories': categories,
    }
    return render(request,'blog/post_list.html', {'posts': posts, 'categories': categories})

def post_detail(request, slug):
    # View for a single blog post
    post = get_object_or_404(Post, slug=slug, status=True)
    return render(request, 'blog/post_detail.html', {'post': post})