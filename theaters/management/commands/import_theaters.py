import csv
from django.core.management.base import BaseCommand, CommandError
from theaters.models import Theater


class Command(BaseCommand):
    help = '劇場データをCSVからインポート'

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
                required = {'name', 'slug'}
                if not required.issubset(set(reader.fieldnames or [])):
                    raise CommandError(f'必須列が不足: {required - set(reader.fieldnames or [])}')

                for i, row in enumerate(reader, start=2):
                    try:
                        slug = row['slug'].strip()
                        if not slug or not row['name'].strip():
                            raise ValueError('name / slug は空にできません')

                        defaults = {
                            'name': row['name'].strip(),
                            'area_name': row.get('area_name', '').strip(),
                            'address': row.get('address', '').strip(),
                            'nearest_station': row.get('nearest_station', '').strip(),
                            'description': row.get('description', '').strip(),
                            'website_url': row.get('website_url', '').strip(),
                            'is_active': row.get('is_active', 'true').strip().lower() in ('true', '1', 'yes'),
                        }

                        if dry_run:
                            self.stdout.write(f'[DRY-RUN] 行{i}: {defaults["name"]} ({slug})')
                        else:
                            _, is_created = Theater.objects.update_or_create(
                                slug=slug, defaults=defaults
                            )
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
