from django.db import migrations


DUPLICATE_THEATERS = [
    ('parco劇場-パルコ劇場', 'parco'),
    ('世田谷文化生活情報センター-世田谷パブリックシアター', 'setagaya-public'),
]


def merge_known_duplicates(apps, schema_editor):
    Theater = apps.get_model('theaters', 'Theater')
    Performance = apps.get_model('works', 'Performance')
    TheaterShop = apps.get_model('shops', 'TheaterShop')

    for duplicate_slug, survivor_slug in DUPLICATE_THEATERS:
        duplicate = Theater.objects.filter(slug=duplicate_slug).first()
        survivor = Theater.objects.filter(slug=survivor_slug).first()
        if duplicate is None or survivor is None:
            continue

        Performance.objects.filter(theater_id=duplicate.id).update(theater_id=survivor.id)

        for link in TheaterShop.objects.filter(theater_id=duplicate.id):
            existing = TheaterShop.objects.filter(
                theater_id=survivor.id,
                shop_id=link.shop_id,
            ).first()
            if existing:
                existing.sort_order = min(existing.sort_order, link.sort_order)
                existing.is_featured = existing.is_featured or link.is_featured
                existing.is_recognized = existing.is_recognized or link.is_recognized
                existing.save(update_fields=['sort_order', 'is_featured', 'is_recognized'])
                link.delete()
            else:
                link.theater_id = survivor.id
                link.save(update_fields=['theater'])

        changed_fields = []
        for field in (
            'area_name', 'address', 'nearest_station', 'description', 'website_url',
            'image', 'image_url', 'google_place_id', 'source_url', 'prefecture', 'city',
        ):
            if not getattr(survivor, field) and getattr(duplicate, field):
                setattr(survivor, field, getattr(duplicate, field))
                changed_fields.append(field)
        if changed_fields:
            survivor.save(update_fields=changed_fields)

        duplicate.delete()


class Migration(migrations.Migration):
    dependencies = [
        ('theaters', '0004_theater_display_order_and_normalize_names'),
        ('shops', '0008_theatershop_is_recognized'),
        ('works', '0006_workeditproposal'),
    ]

    operations = [
        migrations.RunPython(merge_known_duplicates, migrations.RunPython.noop),
    ]
