import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify


def _unique_theater_slug(name):
    base = slugify(name, allow_unicode=True)[:200] or f'theater-{uuid.uuid4().hex[:8]}'
    if not Theater.objects.filter(slug=base).exists():
        return base
    for index in range(2, 1000):
        suffix = f'-{index}'
        candidate = f'{base[:200 - len(suffix)]}{suffix}'
        if not Theater.objects.filter(slug=candidate).exists():
            return candidate
    return f'{base[:187]}-{uuid.uuid4().hex[:8]}'


class Theater(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    area_name = models.CharField(max_length=100, blank=True, default='')
    address = models.CharField(max_length=500, blank=True, default='')
    nearest_station = models.CharField(max_length=200, blank=True, default='')
    description = models.TextField(blank=True, default='')
    website_url = models.URLField(blank=True, default='')
    image = models.ImageField(upload_to='theaters/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, default='')
    google_place_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    source_url = models.URLField(max_length=500, blank=True, default='')
    prefecture = models.CharField(max_length=20, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_theaters',
    )
    is_approved = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_theater_slug(self.name)
        if self.google_place_id == '':
            self.google_place_id = None
        super().save(*args, **kwargs)
