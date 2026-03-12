import csv
from django.core.management.base import BaseCommand, CommandError
from works.models import Work


class Command(BaseCommand):
    help = '作品データをCSVからインポート'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)
        parser.add_argument('--dry-run', action='store_true', help='実際には保存しない')

    def handle(self, *args, **options):
        path = options['csv_file']
        dry_run = options['dry_run']
        created = updated = errors = 0

        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                required = {'title'}
                if not required.issubset(set(reader.fieldnames or [])):
                    raise CommandError(f'必須列が不足: {required - set(reader.fieldnames or [])}')

                for i, row in enumerate(reader, start=2):
                    try:
                        title = row['title'].strip()
                        if not title:
                            raise ValueError('title は空にできません')

                        slug = row.get('slug', '').strip()
                        defaults = {
                            'title': title,
                            'description': row.get('description', '').strip(),
                            'is_approved': True,
                        }

                        if dry_run:
                            self.stdout.write(f'[DRY-RUN] 行{i}: {title} ({slug or "slug自動生成"})')
                        else:
                            if slug:
                                _, is_created = Work.objects.update_or_create(
                                    slug=slug, defaults=defaults
                                )
                            else:
                                # slug がなければ title ベースで検索 or 新規作成
                                existing = Work.objects.filter(title=title).first()
                                if existing:
                                    for k, v in defaults.items():
                                        setattr(existing, k, v)
                                    existing.save()
                                    is_created = False
                                else:
                                    work = Work(**defaults)
                                    work.save()  # slug は save() で自動生成
                                    is_created = True

                            if is_created:
                                created += 1
                            else:
                                updated += 1
                    except Exception as e:
                        errors += 1
                        self.stderr.write(f'行{i}でエラー: {e}')

        except FileNotFoundError:
            raise CommandError(f'ファイルが見つかりません: {path}')

        prefix = '[DRY-RUN] ' if dry_run else ''
        self.stdout.write(self.style.SUCCESS(
            f'{prefix}完了: 作成={created} 更新={updated} エラー={errors}'
        ))
