import csv
from django.core.management.base import BaseCommand, CommandError
from works.models import Work, Performance
from theaters.models import Theater


class Command(BaseCommand):
    help = '公演データをCSVからインポート'

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
                required = {'work_slug', 'theater_slug', 'start_date', 'end_date'}
                if not required.issubset(set(reader.fieldnames or [])):
                    raise CommandError(f'必須列が不足: {required - set(reader.fieldnames or [])}')

                for i, row in enumerate(reader, start=2):
                    try:
                        work_slug = row['work_slug'].strip()
                        theater_slug = row['theater_slug'].strip()
                        start_date = row['start_date'].strip()
                        end_date = row['end_date'].strip()

                        if not all([work_slug, theater_slug, start_date, end_date]):
                            raise ValueError('work_slug, theater_slug, start_date, end_date は必須です')

                        try:
                            work = Work.objects.get(slug=work_slug)
                        except Work.DoesNotExist:
                            raise ValueError(f'作品 {work_slug} が見つかりません')

                        try:
                            theater = Theater.objects.get(slug=theater_slug)
                        except Theater.DoesNotExist:
                            raise ValueError(f'劇場 {theater_slug} が見つかりません')

                        defaults = {
                            'company_name': row.get('company_name', '').strip(),
                            'start_date': start_date,
                            'end_date': end_date,
                            'note': row.get('note', '').strip(),
                            'is_approved': True,
                        }

                        if dry_run:
                            self.stdout.write(
                                f'[DRY-RUN] 行{i}: {work_slug} @ {theater_slug} ({start_date}〜{end_date})'
                            )
                        else:
                            _, is_created = Performance.objects.update_or_create(
                                work=work, theater=theater, start_date=start_date,
                                defaults=defaults
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
