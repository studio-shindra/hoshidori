from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('works', '0005_performance_optional_dates'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkEditProposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changes', models.JSONField(default=dict)),
                ('status', models.CharField(choices=[('pending', '確認待ち'), ('approved', '反映済み'), ('rejected', '見送り')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('performance', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='edit_proposals', to='works.performance')),
                ('proposed_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_edit_proposals', to=settings.AUTH_USER_MODEL)),
                ('work', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='edit_proposals', to='works.work')),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
