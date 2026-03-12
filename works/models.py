from django.conf import settings
from django.db import models


class Work(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
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

    def __str__(self):
        return self.title


class Person(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
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
