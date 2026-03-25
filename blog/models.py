from django.db import models
from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    body = models.TextField()
    image = models.ImageField(upload_to='blog_pics/%Y/%m/%d/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False) # False = Draft, True = Published

    def __str__(self):
        return self.title