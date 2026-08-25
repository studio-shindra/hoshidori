from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reviews', '0006_viewinglog_after_shop'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[('spam', 'スパム・宣伝'), ('harassment', '嫌がらせ・誹謗中傷'), ('hate', '差別的な表現'), ('sexual', '性的・不適切な内容'), ('copyright', '権利侵害'), ('other', 'その他')], max_length=20)),
                ('details', models.TextField(blank=True, default='')),
                ('status', models.CharField(choices=[('pending', '確認待ち'), ('resolved', '対応済み'), ('dismissed', '問題なし')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_reports', to=settings.AUTH_USER_MODEL)),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='reviews.review')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='UserBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('blocked', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocked_by_users', to=settings.AUTH_USER_MODEL)),
                ('blocker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_blocks', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.AddConstraint(
            model_name='reviewreport',
            constraint=models.UniqueConstraint(fields=('reporter', 'review'), name='unique_reporter_review'),
        ),
        migrations.AddConstraint(
            model_name='userblock',
            constraint=models.UniqueConstraint(fields=('blocker', 'blocked'), name='unique_user_block'),
        ),
    ]
