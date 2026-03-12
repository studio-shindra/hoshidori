import csv
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from shops.models import Shop, TheaterShop
from theaters.models import Theater

User = get_user_model()


class Command(BaseCommand):
    help = '店舗データをCSVからインポート'

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

                        owner = None
                        owner_username = row.get('owner_username', '').strip()
                        if owner_username:
                            try:
                                owner = User.objects.get(username=owner_username)
                            except User.DoesNotExist:
                                self.stderr.write(f'行{i}: ユーザー {owner_username} が見つかりません（スキップせず続行）')

                        defaults = {
                            'name': row['name'].strip(),
                            'category': row.get('category', '').strip(),
                            'description': row.get('description', '').strip(),
                            'address': row.get('address', '').strip(),
                            'nearest_station': row.get('nearest_station', '').strip(),
                            'distance_note': row.get('distance_note', '').strip(),
                            'website_url': row.get('website_url', '').strip(),
                            'instagram_url': row.get('instagram_url', '').strip(),
                            'tabelog_url': row.get('tabelog_url', '').strip(),
                            'google_map_url': row.get('google_map_url', '').strip(),
                            'phone_number': row.get('phone_number', '').strip(),
                            'opening_hours_text': row.get('opening_hours_text', '').strip(),
                            'benefit_text': row.get('benefit_text', '').strip(),
                            'is_active': row.get('is_active', 'true').strip().lower() in ('true', '1', 'yes'),
                        }
                        if owner:
                            defaults['owner'] = owner

                        if dry_run:
                            self.stdout.write(f'[DRY-RUN] 行{i}: {defaults["name"]} ({slug})')
                        else:
                            shop, is_created = Shop.objects.update_or_create(
                                slug=slug, defaults=defaults
                            )
                            if is_created:
                                created += 1
                            else:
                                updated += 1

                            # TheaterShop 紐付け
                            theater_slug = row.get('theater_slug', '').strip()
                            if theater_slug:
                                try:
                                    theater = Theater.objects.get(slug=theater_slug)
                                    sort_order = int(row.get('sort_order', '0').strip() or '0')
                                    is_featured = row.get('is_featured', 'false').strip().lower() in ('true', '1', 'yes')
                                    TheaterShop.objects.update_or_create(
                                        theater=theater, shop=shop,
                                        defaults={'sort_order': sort_order, 'is_featured': is_featured}
                                    )
                                except Theater.DoesNotExist:
                                    self.stderr.write(f'行{i}: 劇場 {theater_slug} が見つかりません')

                    except Exception as e:
                        errors += 1
                        self.stderr.write(f'行{i}でエラー: {e}')

        except FileNotFoundError:
            raise CommandError(f'ファイルが見つかりません: {path}')

        prefix = '[DRY-RUN] ' if dry_run else ''
        self.stdout.write(self.style.SUCCESS(
            f'{prefix}完了: 作成={created} 更新={updated} エラー={errors}'
        ))
