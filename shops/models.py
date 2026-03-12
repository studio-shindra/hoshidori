from django.conf import settings
from django.db import models


class Shop(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField(blank=True, default='')
    address = models.CharField(max_length=255, blank=True, default='')
    nearest_station = models.CharField(max_length=100, blank=True, default='')
    distance_note = models.CharField(max_length=255, blank=True, default='')
    website_url = models.URLField(blank=True, default='')
    instagram_url = models.URLField(blank=True, default='')
    tabelog_url = models.URLField(blank=True, default='')
    google_map_url = models.URLField(blank=True, default='')
    phone_number = models.CharField(max_length=50, blank=True, default='')
    opening_hours_text = models.TextField(blank=True, default='')
    benefit_text = models.TextField(blank=True, default='')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='owned_shops',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class TheaterShop(models.Model):
    theater = models.ForeignKey(
        'theaters.Theater', on_delete=models.CASCADE, related_name='theater_shops',
    )
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='theater_shops')
    sort_order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    class Meta:
        unique_together = ['theater', 'shop']
        ordering = ['sort_order']

    def __str__(self):
        return f'{self.theater.name} - {self.shop.name}'


class Coupon(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='coupons')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    discount_text = models.CharField(max_length=255)
    conditions = models.TextField(blank=True, default='')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class CouponUseLog(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='use_logs')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='coupon_uses',
    )
    performance = models.ForeignKey(
        'works.Performance', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='coupon_uses',
    )
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-used_at']

    def __str__(self):
        return f'{self.user} used {self.coupon.title}'


class ShopClickLog(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='click_logs')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='shop_clicks',
    )
    source_type = models.CharField(max_length=50)
    clicked_target = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class ShopPlan(models.Model):
    name = models.CharField(max_length=100)
    monthly_price = models.IntegerField()
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['monthly_price']

    def __str__(self):
        return self.name


class ShopSubscription(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(ShopPlan, on_delete=models.CASCADE, related_name='subscriptions')
    status = models.CharField(max_length=50)
    stripe_customer_id = models.CharField(max_length=255, blank=True, default='')
    stripe_subscription_id = models.CharField(max_length=255, blank=True, default='')
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.shop.name} - {self.plan.name}'
