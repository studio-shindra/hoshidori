from django.db import migrations, models


FULL_WIDTH_ASCII = str.maketrans(
    {chr(code): chr(code - 0xFEE0) for code in range(0xFF01, 0xFF5F)}
    | {'\u3000': ' '}
)


FAMOUS_THEATERS = [
    '本多劇場',
    '新国立劇場',
    '東京芸術劇場',
    'PARCO劇場',
    '帝国劇場',
    '日生劇場',
    'シアタークリエ',
    '世田谷パブリックシアター',
    '紀伊國屋ホール',
    '紀伊國屋サザンシアター',
    'Bunkamura',
    '明治座',
    '東京宝塚劇場',
    'サンシャイン劇場',
    '銀河劇場',
    '新橋演舞場',
    '歌舞伎座',
    '博品館劇場',
    'THEATER MILANO-Za',
    'Brillia HALL',
]


def normalize_and_rank(apps, schema_editor):
    Theater = apps.get_model('theaters', 'Theater')
    for theater in Theater.objects.all().only('id', 'name'):
        normalized = theater.name.translate(FULL_WIDTH_ASCII).strip()
        order = 1000
        for index, keyword in enumerate(FAMOUS_THEATERS, start=1):
            if keyword.casefold() in normalized.casefold():
                order = index * 10
                break
        if normalized != theater.name or theater.display_order != order:
            Theater.objects.filter(pk=theater.pk).update(
                name=normalized,
                display_order=order,
            )


class Migration(migrations.Migration):
    dependencies = [
        ('theaters', '0003_theater_city_theater_created_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='theater',
            name='display_order',
            field=models.PositiveIntegerField(db_index=True, default=1000),
        ),
        migrations.RunPython(normalize_and_rank, migrations.RunPython.noop),
        migrations.AlterModelOptions(
            name='theater',
            options={'ordering': ['display_order', 'name', 'id']},
        ),
    ]
