from django.db import migrations


def deactivate_coupons(apps, schema_editor):
    Coupon = apps.get_model('shops', 'Coupon')
    Coupon.objects.update(is_active=False)


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0005_add_shop_want_to_go'),
    ]

    operations = [
        migrations.RunPython(deactivate_coupons, migrations.RunPython.noop),
    ]
