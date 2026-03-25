from django.db import models
from django.db import models

class About(models.Model):
    title = models.CharField(max_length=200, default="About Our Store")
    content = models.TextField()
    image = models.ImageField(upload_to='about/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta:
        verbose_name_plural = "About Us"

    def __str__(self):
        return self.title