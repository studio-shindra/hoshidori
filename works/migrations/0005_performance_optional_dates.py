from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('works', '0004_postersubmission_cloudinary_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='performance',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='performance',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
