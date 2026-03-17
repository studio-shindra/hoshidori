from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0003_add_shop_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='shop',
            name='featured_order',
            field=models.IntegerField(default=0),
        ),
    ]
