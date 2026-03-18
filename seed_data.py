"""
仮データ投入スクリプト
python3 manage.py shell < seed_data.py
"""
import datetime
from accounts.models import User
from theaters.models import Theater
from works.models import Work, Performance, PosterSubmission
from reviews.models import ViewingLog, Review

user = User.objects.get(username='admin')

# --- 既存の作品関連データをクリア ---
Review.objects.all().delete()
ViewingLog.objects.all().delete()
PosterSubmission.objects.all().delete()
Performance.objects.all().delete()
Work.objects.all().delete()
print('Cleared existing works data')

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

# --- Works & Performances (20本) ---
works_data = [
    # (タイトル, 劇場index, 開始日, 終了日, status, 観た日)
    ('星降る夜のワルツ',       0, '2026-01-10', '2026-02-15', 'watched',  '2026-01-25'),
    ('ガラスの迷宮',           1, '2025-11-01', '2025-12-28', 'watched',  '2025-11-20'),
    ('さよならの先へ',         2, '2026-02-01', '2026-03-10', 'watched',  '2026-02-14'),
    ('月曜日のピエロ',         0, '2026-01-05', '2026-02-28', 'watched',  '2026-01-30'),
    ('約束の庭',               1, '2026-03-15', '2026-05-10', 'planned',  None),
    ('嵐のあとで',             2, '2026-04-01', '2026-05-31', 'planned',  None),
    ('夜明けのレッスン',       0, '2026-04-10', '2026-05-20', 'planned',  None),
    ('水色の手紙',             1, '2026-05-01', '2026-06-30', 'planned',  None),
    ('花と嘘と秘密',           2, '2026-05-15', '2026-07-01', 'planned',  None),
    ('路地裏のセレナーデ',     0, '2026-06-01', '2026-07-15', 'planned',  None),
    ('雨の日の天使',           1, '2026-06-10', '2026-08-01', 'planned',  None),
    ('銀色のカーテンコール',   2, '2026-07-01', '2026-08-31', 'planned',  None),
    ('虹を渡る人',             0, '2026-08-01', '2026-09-15', 'planned',  None),
    ('風の忘れもの',           1, '2026-08-15', '2026-09-30', 'planned',  None),
    ('真夜中の図書館',         2, '2026-09-01', '2026-10-15', 'planned',  None),
    ('時をかける旅人',         0, '2026-09-20', '2026-11-01', 'planned',  None),
    ('黄昏のダンスホール',     1, '2026-10-01', '2026-11-15', 'planned',  None),
    ('海辺の椅子',             2, '2026-10-15', '2026-11-30', 'planned',  None),
    ('鏡の中の街',             0, '2026-11-01', '2026-12-15', 'planned',  None),
    ('窓辺のアリア',           1, '2026-11-15', '2026-12-31', 'planned',  None),
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

# --- Posters (サンプルポスター画像) ---
poster_urls = [
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773818756/f-01_cymgcg.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773818756/f-02_wmbepd.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773818756/f-03_sahsdd.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773818755/f-04_b5q4ec.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773818756/f-05_fex9rf.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773818756/f-06_gozpyo.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773819696/f-08_enfjal.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773819696/f-09_j324h0.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773819695/f-10_gmzvwz.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773819697/f-11_g3qyro.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773819697/f-12_bukcuw.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773819698/f-13_duv3ng.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773819699/f-14_dcwhkj.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773819697/f-15_esedn7.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773819704/f-16_j6ydwm.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773819699/f-17_egirbj.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773819699/f-18_vuy0ag.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773819699/f-19_qapv85.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773819700/f-20_biaqdp.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773819909/f-21_nfqd2b.png',
]
poster_public_ids = [
    'f-01_cymgcg', 'f-02_wmbepd', 'f-03_sahsdd',
    'f-04_b5q4ec', 'f-05_fex9rf', 'f-06_gozpyo',
    'f-08_enfjal', 'f-09_j324h0', 'f-10_gmzvwz',
    'f-11_g3qyro', 'f-12_bukcuw', 'f-13_duv3ng',
    'f-14_dcwhkj', 'f-15_esedn7', 'f-16_j6ydwm',
    'f-17_egirbj', 'f-18_vuy0ag', 'f-19_qapv85',
    'f-20_biaqdp', 'f-21_nfqd2b',
]

works_all = list(Work.objects.order_by('id'))
for i, work in enumerate(works_all):
    url = poster_urls[i % len(poster_urls)]
    public_id = poster_public_ids[i % len(poster_public_ids)]
    PosterSubmission.objects.get_or_create(
        work=work,
        user=user,
        defaults={
            'image_url': url,
            'image_public_id': public_id,
            'image_width': 600,
            'image_height': 900,
            'image_format': 'png',
            'is_selected': True,
        },
    )

planned = ViewingLog.objects.filter(user=user, status='planned').count()
watched = ViewingLog.objects.filter(user=user, status='watched').count()
print(f'Done! planned={planned}, watched={watched}, posters={PosterSubmission.objects.count()}')
