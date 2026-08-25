import csv
from django.core.management.base import BaseCommand, CommandError
from theaters.models import Theater
from theaters.text import normalize_theater_name


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
                            'name': normalize_theater_name(row['name']),
                            'area_name': row.get('area_name', '').strip(),
                            'address': row.get('address', '').strip(),
                            'nearest_station': row.get('nearest_station', '').strip(),
                            'description': row.get('description', '').strip(),
                            'website_url': row.get('website_url', '').strip(),
                            'source_url': row.get('source_url', '').strip(),
                            'prefecture': row.get('prefecture', '').strip(),
                            'city': row.get('city', '').strip(),
                            'google_place_id': row.get('google_place_id', '').strip() or None,
                            'is_approved': row.get('is_approved', 'true').strip().lower() in ('true', '1', 'yes'),
                            'is_active': row.get('is_active', 'true').strip().lower() in ('true', '1', 'yes'),
                            'display_order': int(row.get('display_order', '1000').strip() or '1000'),
                        }

                        if dry_run:
                            self.stdout.write(f'[DRY-RUN] 行{i}: {defaults["name"]} ({slug})')
                        else:
                            theater = Theater.objects.filter(slug=slug).first()
                            if theater is None:
                                theater = Theater.objects.filter(name__iexact=defaults['name']).first()

                            if theater is None:
                                Theater.objects.create(slug=slug, **defaults)
                                created += 1
                            else:
                                # 既存のサンプルや人手で補った説明を、空欄で消さない。
                                for field, value in defaults.items():
                                    if value not in ('', None):
                                        setattr(theater, field, value)
                                theater.save()
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
