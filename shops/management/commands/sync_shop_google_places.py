from django.core.management.base import BaseCommand

from shops.google_places import search_shop_place
from shops.models import Shop


class Command(BaseCommand):
    help = '店舗名と住所からGoogle Placesの店舗IDとGoogle Maps URLを同期'

    def add_arguments(self, parser):
        parser.add_argument('--slug', action='append', default=[])
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        shops = Shop.objects.filter(is_active=True).order_by('name')
        if options['slug']:
            shops = shops.filter(slug__in=options['slug'])

        synced = missing = 0
        for shop in shops:
            place = search_shop_place(shop)
            if not place or not place.get('place_id'):
                missing += 1
                self.stderr.write(f'見つかりません: {shop.name}')
                continue

            self.stdout.write(
                f"{shop.name}: {place['place_id']} / {place.get('name', '')}"
            )
            if not options['dry_run']:
                Shop.objects.filter(pk=shop.pk).update(
                    google_place_id=place['place_id'],
                    google_map_url=place.get('google_maps_uri') or shop.google_map_url,
                )
            synced += 1

        prefix = '[DRY-RUN] ' if options['dry_run'] else ''
        self.stdout.write(self.style.SUCCESS(
            f'{prefix}完了: 同期={synced} 未検出={missing}'
        ))
