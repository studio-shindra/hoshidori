from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews',
    )
    performance = models.ForeignKey(
        'works.Performance', on_delete=models.CASCADE, related_name='reviews',
    )
    title = models.CharField(max_length=200, blank=True, default='')
    body = models.TextField()
    rating_overall = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    is_spoiler = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.performance}'


class ViewingLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='viewing_logs',
    )
    performance = models.ForeignKey(
        'works.Performance', on_delete=models.CASCADE, related_name='viewing_logs',
    )
    watched_on = models.DateField()
    memo = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-watched_on']

    def __str__(self):
        return f'{self.user} - {self.performance} ({self.watched_on})'
