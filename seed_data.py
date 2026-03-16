"""
仮データ投入スクリプト
python3 manage.py shell < seed_data.py
"""
import datetime
from accounts.models import User
from theaters.models import Theater
from works.models import Work, Performance
from reviews.models import ViewingLog

user = User.objects.get(username='admin')

# --- Theaters ---
theaters_data = [
    ('新国立劇場', 'shin-kokuritsu', '初台', '東京都渋谷区本町1-1-1'),
    ('シアタークリエ', 'theatre-creathre', '日比谷', '東京都千代田区有楽町2-5-1'),
    ('天王洲 銀河劇場', 'galaxy-theatre', '天王洲アイル', '東京都品川区東品川2-1-3'),
]
theaters = []
for name, slug, area, address in theaters_data:
    t, _ = Theater.objects.get_or_create(slug=slug, defaults={'name': name, 'area_name': area, 'address': address})
    theaters.append(t)

# --- Works & Performances (13本) ---
works_data = [
    # (タイトル, 劇場index, 開始日, 終了日, status, 観た日)
    ('レ・ミゼラブル',       0, '2026-01-10', '2026-02-15', 'watched',  '2026-01-25'),
    ('キャッツ',             1, '2025-11-01', '2025-12-28', 'watched',  '2025-11-20'),
    ('ミス・サイゴン',       2, '2026-02-01', '2026-03-10', 'watched',  '2026-02-14'),
    ('オペラ座の怪人',       0, '2026-01-05', '2026-02-28', 'watched',  '2026-01-30'),
    ('ウィキッド',           1, '2026-03-15', '2026-05-10', 'planned',  None),
    ('ハミルトン',           2, '2026-04-01', '2026-05-31', 'planned',  None),
    ('マリー・キュリー',     0, '2026-04-10', '2026-05-20', 'planned',  None),
    ('エリザベート',         1, '2026-05-01', '2026-06-30', 'planned',  None),
    ('アナスタシア',         2, '2026-05-15', '2026-07-01', 'planned',  None),
    ('ロミオ＆ジュリエット', 0, '2026-06-01', '2026-07-15', 'planned',  None),
    ('モーツァルト！',       1, '2026-06-10', '2026-08-01', 'planned',  None),
    ('RENT',                 2, '2026-07-01', '2026-08-31', 'planned',  None),
    ('スウィーニー・トッド', 0, '2026-08-01', '2026-09-15', 'planned',  None),
]

for title, theater_idx, start, end, status, watched_on in works_data:
    work, _ = Work.objects.get_or_create(title=title, defaults={'created_by': user})
    perf, _ = Performance.objects.get_or_create(
        work=work,
        theater=theaters[theater_idx],
        start_date=start,
        defaults={
            'end_date': end,
            'is_approved': True,
            'created_by': user,
        },
    )
    ViewingLog.objects.get_or_create(
        user=user,
        performance=perf,
        defaults={
            'status': status,
            'watched_on': datetime.date.fromisoformat(watched_on) if watched_on else None,
        },
    )

planned = ViewingLog.objects.filter(user=user, status='planned').count()
watched = ViewingLog.objects.filter(user=user, status='watched').count()
print(f'Done! planned={planned}, watched={watched}')
