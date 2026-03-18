from django.db import models


class Theater(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    area_name = models.CharField(max_length=100, blank=True, default='')
    address = models.CharField(max_length=500, blank=True, default='')
    nearest_station = models.CharField(max_length=200, blank=True, default='')
    description = models.TextField(blank=True, default='')
    website_url = models.URLField(blank=True, default='')
    image = models.ImageField(upload_to='theaters/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
