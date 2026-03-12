from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('works', '0003_alter_person_slug_alter_work_slug_postersubmission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postersubmission',
            name='image',
            field=models.ImageField(blank=True, default='', upload_to='posters/'),
        ),
        migrations.AddField(
            model_name='postersubmission',
            name='image_url',
            field=models.URLField(blank=True, default='', max_length=500),
        ),
        migrations.AddField(
            model_name='postersubmission',
            name='image_public_id',
            field=models.CharField(blank=True, default='', max_length=300),
        ),
        migrations.AddField(
            model_name='postersubmission',
            name='image_width',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='postersubmission',
            name='image_height',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='postersubmission',
            name='image_format',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
    ]
