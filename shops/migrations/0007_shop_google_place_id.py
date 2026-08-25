from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0006_deactivate_legacy_coupons'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='google_place_id',
            field=models.CharField(blank=True, db_index=True, default='', max_length=255),
        ),
    ]
