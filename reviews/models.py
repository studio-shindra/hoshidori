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
    RATING_CHOICES = [
        (3, '観た'),
        (4, '良かった'),
        (5, '最高'),
    ]
    rating_overall = models.PositiveSmallIntegerField(
        null=True, blank=True,
        choices=RATING_CHOICES,
        validators=[MinValueValidator(3), MaxValueValidator(5)],
    )
    is_spoiler = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.performance}'


class ViewingLog(models.Model):
    STATUS_CHOICES = [
        ('watched', '観た'),
        ('planned', 'これから観る'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='viewing_logs',
    )
    performance = models.ForeignKey(
        'works.Performance', on_delete=models.CASCADE, related_name='viewing_logs',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='watched')
    watched_on = models.DateField(null=True, blank=True)
    watched_time = models.TimeField(null=True, blank=True)
    memo = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'performance'], name='unique_user_performance'),
        ]

    def __str__(self):
        return f'{self.user} - {self.performance} ({self.get_status_display()})'


class ViewingLogImage(models.Model):
    viewing_log = models.ForeignKey(
        ViewingLog, on_delete=models.CASCADE, related_name='images',
    )
    image_url = models.URLField(max_length=500)
    image_public_id = models.CharField(max_length=300, blank=True, default='')
    image_width = models.IntegerField(null=True, blank=True)
    image_height = models.IntegerField(null=True, blank=True)
    image_format = models.CharField(max_length=20, blank=True, default='')
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f'Image #{self.id} for {self.viewing_log}'


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes',
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='likes',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'review']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} → {self.review}'
