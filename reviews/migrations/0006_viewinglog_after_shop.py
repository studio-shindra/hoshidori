from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0005_viewing_log_image'),
        ('shops', '0005_add_shop_want_to_go'),
    ]

    operations = [
        migrations.AddField(
            model_name='viewinglog',
            name='after_shop',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='after_viewing_logs',
                to='shops.shop',
            ),
        ),
    ]
