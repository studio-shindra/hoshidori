import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify


def _unique_slug(model_class, base, slug_field='slug', max_length=300):
    slug = slugify(base, allow_unicode=True)[:max_length] or f'item-{uuid.uuid4().hex[:8]}'
    if not model_class.objects.filter(**{slug_field: slug}).exists():
        return slug
    for i in range(2, 1000):
        candidate = f'{slug[:max_length - len(str(i)) - 1]}-{i}'
        if not model_class.objects.filter(**{slug_field: candidate}).exists():
            return candidate
    return f'{slug[:max_length - 13]}-{uuid.uuid4().hex[:8]}'


class Work(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_works',
    )
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(Work, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Person(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    phonetic = models.CharField(max_length=200, blank=True, default='')
    profile_text = models.TextField(blank=True, default='')
    sns_url = models.URLField(blank=True, default='')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_people',
    )
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'people'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(Person, self.name, max_length=200)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Performance(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='performances')
    theater = models.ForeignKey(
        'theaters.Theater', on_delete=models.CASCADE, related_name='performances',
    )
    company_name = models.CharField(max_length=200, blank=True, default='')
    start_date = models.DateField()
    end_date = models.DateField()
    note = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_performances',
    )
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.work.title} @ {self.theater.name}'


class PerformanceCast(models.Model):
    performance = models.ForeignKey(
        Performance, on_delete=models.CASCADE, related_name='casts',
    )
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='casts')
    role_name = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['performance', 'person']
        ordering = ['id']

    def __str__(self):
        return f'{self.person.name} ({self.role_name})' if self.role_name else self.person.name


class PosterSubmission(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='poster_submissions')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='poster_submissions',
    )
    image = models.ImageField(upload_to='posters/', blank=True, default='')
    # Cloudinary fields
    image_url = models.URLField(max_length=500, blank=True, default='')
    image_public_id = models.CharField(max_length=300, blank=True, default='')
    image_width = models.IntegerField(null=True, blank=True)
    image_height = models.IntegerField(null=True, blank=True)
    image_format = models.CharField(max_length=20, blank=True, default='')
    caption = models.CharField(max_length=500, blank=True, default='')
    is_selected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.is_selected:
            PosterSubmission.objects.filter(
                work=self.work, is_selected=True,
            ).exclude(pk=self.pk).update(is_selected=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.work.title} - {self.user}'
