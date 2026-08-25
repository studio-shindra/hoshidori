from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('shops', '0007_shop_google_place_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='theatershop',
            name='is_recognized',
            field=models.BooleanField(default=False),
        ),
    ]
