from django.db import migrations


def set_recognized_shop_display_order(apps, schema_editor):
    Shop = apps.get_model('shops', 'Shop')
    Shop.objects.filter(slug='kanmidokoro-shimokitazawa').update(featured_order=1)
    Shop.objects.filter(slug='il-legame-mejiro').update(featured_order=2)


def reset_recognized_shop_display_order(apps, schema_editor):
    Shop = apps.get_model('shops', 'Shop')
    Shop.objects.filter(
        slug__in=['kanmidokoro-shimokitazawa', 'il-legame-mejiro'],
    ).update(featured_order=0)


class Migration(migrations.Migration):
    dependencies = [
        ('shops', '0008_theatershop_is_recognized'),
    ]

    operations = [
        migrations.RunPython(
            set_recognized_shop_display_order,
            reset_recognized_shop_display_order,
        ),
    ]
