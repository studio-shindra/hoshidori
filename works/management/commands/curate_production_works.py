from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q

from reviews.models import Review, ViewingLog
from theaters.models import Theater
from works.models import Performance, PerformanceCast, Person, Work


WORK_SPECS = [
    {
        'title': 'パラダイス・エフェクト',
        'slug': 'パラダイスエフェクト',
        'aliases': ['パラダイス・エフェクト', 'パラダイスエフェクト'],
        'description': '小柳心、第一回単独公演。一人芝居オムニバス短編集。',
        'performances': [
            {
                'theater_slug': '新生館スタジオ',
                'company_name': 'コヤナギシン',
                'start_date': '2026-05-22',
                'end_date': '2026-05-24',
                'note': '全5公演／全席4,800円',
                'casts': ['小柳心'],
            },
        ],
    },
    {
        'title': 'うま－馬に乗ってこの世の外へ－',
        'slug': 'uma-uma-ni-notte-kono-yo-no-soto-e',
        'aliases': ['うま－馬に乗ってこの世の外へ－', '舞台うま'],
        'description': '井上ひさしの未上演戯曲を、藤田俊太郎の演出で初演。',
        'performances': [
            {
                'theater_slug': 'parco',
                'company_name': 'PARCO PRODUCE 2026',
                'start_date': '2026-07-08',
                'end_date': '2026-07-28',
                'note': '作：井上ひさし／演出：藤田俊太郎',
                'casts': [
                    '小瀧望', '音月桂', '加藤梨里香', '大鶴佐助', '小松利昌',
                    '小林きな子', '小柳心', '尾倉ケント', '森加織', '安井順平', '梅沢昌代',
                ],
            },
            {
                'theater_slug': 'sky-theater-mbs',
                'theater_defaults': {
                    'name': 'SkyシアターMBS',
                    'address': '大阪府大阪市北区梅田3-2-2 JPタワー大阪6F',
                    'area_name': '梅田',
                    'prefecture': '大阪府',
                    'city': '大阪市北区',
                    'website_url': 'https://stm-mle.jp/',
                    'is_approved': True,
                    'is_active': True,
                },
                'company_name': 'PARCO PRODUCE 2026',
                'start_date': '2026-08-06',
                'end_date': '2026-08-12',
                'note': '作：井上ひさし／演出：藤田俊太郎',
                'casts': [
                    '小瀧望', '音月桂', '加藤梨里香', '大鶴佐助', '小松利昌',
                    '小林きな子', '小柳心', '尾倉ケント', '森加織', '安井順平', '梅沢昌代',
                ],
            },
        ],
    },
    {
        'title': 'いつかアイツに会いに行く -BEYOND THE MOON-',
        'slug': 'itsuka-aitsu-ni-ai-ni-iku-beyond-the-moon',
        'aliases': ['いつかアイツに会いに行く -BEYOND THE MOON-', 'いつかアイツに会いに行く-BEYOND THE MOON-'],
        'description': '「会いたい」という想いにひたむきに突き進む、ロードムービー演劇。',
        'performances': [
            {
                'theater_slug': '紀伊國屋サザンシアターtakashimaya',
                'company_name': 'ニッポン放送',
                'start_date': '2026-09-03',
                'end_date': '2026-09-08',
                'note': '演出・音楽・原案：小林顕作／脚本：渡辺雄介・木乃江祐希',
                'casts': [
                    '䋝田圭亮', '梶原善', '河田陽菜', '小柳心', '澤田育子',
                    '千代田信一', '富岡晃一郎', '中村哲人', '福永マリカ',
                ],
            },
            {
                'theater_slug': '博品館劇場',
                'company_name': 'ニッポン放送',
                'start_date': '2026-09-11',
                'end_date': '2026-09-22',
                'note': '演出・音楽・原案：小林顕作／脚本：渡辺雄介・木乃江祐希',
                'casts': [
                    '䋝田圭亮', '梶原善', '河田陽菜', '小柳心', '澤田育子',
                    '千代田信一', '富岡晃一郎', '中村哲人', '福永マリカ',
                ],
            },
        ],
    },
]


class Command(BaseCommand):
    help = '本番の作品を公式情報に基づく指定3作品へ整理する'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply', action='store_true',
            help='指定時のみ、本番データを更新し、それ以外の作品を削除する',
        )

    def handle(self, *args, **options):
        keep_query = Q()
        for spec in WORK_SPECS:
            keep_query |= Q(slug=spec['slug']) | Q(title__in=spec['aliases'])
        delete_qs = Work.objects.exclude(keep_query)
        delete_titles = list(delete_qs.order_by('id').values_list('title', flat=True))
        log_count = ViewingLog.objects.filter(performance__work__in=delete_qs).count()
        review_count = Review.objects.filter(performance__work__in=delete_qs).count()

        self.stdout.write('残す作品:')
        for spec in WORK_SPECS:
            self.stdout.write(f"  - {spec['title']}")
        self.stdout.write(f'削除対象: {len(delete_titles)}作品 / 観劇記録 {log_count}件 / 感想 {review_count}件')
        for title in delete_titles:
            self.stdout.write(f'  - {title}')

        if not options['apply']:
            self.stdout.write(self.style.WARNING('確認のみ。反映するには --apply を付けて実行してください。'))
            return

        with transaction.atomic():
            kept_ids = []
            for spec in WORK_SPECS:
                work = Work.objects.filter(title__in=spec['aliases']).order_by('id').first()
                if work is None:
                    work = Work.objects.filter(slug=spec['slug']).first()
                if work is None:
                    work = Work()
                work.title = spec['title']
                work.slug = spec['slug']
                work.description = spec['description']
                work.is_approved = True
                work.save()
                kept_ids.append(work.id)

                retained_performance_ids = []
                existing_performances = list(work.performances.order_by('id'))
                for index, performance_spec in enumerate(spec['performances']):
                    theater_defaults = performance_spec.get('theater_defaults')
                    if theater_defaults:
                        theater, _ = Theater.objects.update_or_create(
                            slug=performance_spec['theater_slug'],
                            defaults=theater_defaults,
                        )
                    else:
                        try:
                            theater = Theater.objects.get(slug=performance_spec['theater_slug'])
                        except Theater.DoesNotExist as error:
                            raise CommandError(
                                f"劇場が見つかりません: {performance_spec['theater_slug']}"
                            ) from error

                    performance = existing_performances[index] if index < len(existing_performances) else Performance(work=work)
                    performance.theater = theater
                    performance.company_name = performance_spec['company_name']
                    performance.start_date = performance_spec['start_date']
                    performance.end_date = performance_spec['end_date']
                    performance.note = performance_spec['note']
                    performance.is_approved = True
                    performance.save()
                    retained_performance_ids.append(performance.id)

                    cast_names = performance_spec['casts']
                    PerformanceCast.objects.filter(performance=performance).exclude(
                        person__name__in=cast_names,
                    ).delete()
                    for person_name in cast_names:
                        person, _ = Person.objects.get_or_create(
                            name=person_name,
                            defaults={'is_approved': True},
                        )
                        if not person.is_approved:
                            person.is_approved = True
                            person.save(update_fields=['is_approved', 'updated_at'])
                        PerformanceCast.objects.update_or_create(
                            performance=performance,
                            person=person,
                            defaults={'role_name': ''},
                        )

                work.performances.exclude(id__in=retained_performance_ids).delete()

            Work.objects.exclude(id__in=kept_ids).delete()
            Person.objects.filter(casts__isnull=True).delete()

        self.stdout.write(self.style.SUCCESS(
            f'反映完了: 作品 {Work.objects.count()}件 / 出演者 {Person.objects.count()}件 / '
            f'公演 {Performance.objects.count()}件'
        ))
