import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from shops.models import Shop, TheaterShop, Coupon
from theaters.models import Theater

# ---- Shop images (4枚をローテーション) ----
SHOP_IMAGES = [
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773821418/s-01_kbmwjk.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773821419/s-02_el6z2s.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773821418/s-03_tu4ciy.png',
    'https://res.cloudinary.com/dbvisrqec/image/upload/v1773821419/s-04_swxomm.png',
]

# ---- Shops (4店舗) ----
shops_data = [
    {
        'name': 'カフェ・ド・クリエ 日比谷店',
        'slug': 'cafe-de-crie-hibiya',
        'category': 'カフェ',
        'description': '日比谷エリアの観劇ファン御用達カフェ。開演前の待ち合わせスポットとして定番。モーニングからディナーまで幅広く対応。',
        'address': '東京都千代田区有楽町1-2-2 日比谷シャンテ B1F',
        'nearest_station': '日比谷駅',
        'distance_note': '日比谷駅直結／帝国劇場から徒歩2分',
        'opening_hours_text': '8:00〜22:00',
        'benefit_text': 'ケーキセット100円引き（半券提示）',
        'is_featured': True,
        'featured_order': 1,
        'theaters': ['teikoku', 'nissei', 'theatre-crea', 'tokyo-takarazuka'],
    },
    {
        'name': 'サイゼリヤ オペラシティ店',
        'slug': 'saizeriya-operacity',
        'category': 'レストラン',
        'description': '東京オペラシティ地下のイタリアンレストラン。劇場直結でアクセス抜群。リーズナブルにしっかり食事ができる。',
        'address': '東京都新宿区西新宿3-20-2 東京オペラシティ B1F',
        'nearest_station': '初台駅',
        'distance_note': '新国立劇場直結',
        'opening_hours_text': '11:00〜22:00（L.O. 21:30）',
        'benefit_text': '観劇割あり（チケット半券提示で全品5%OFF）',
        'is_featured': True,
        'featured_order': 2,
        'theaters': ['shin-kokuritsu'],
    },
    {
        'name': 'T.Y.HARBOR',
        'slug': 'ty-harbor',
        'category': 'ブルワリーレストラン',
        'description': '天王洲の水辺に佇むブルワリーレストラン。自家醸造クラフトビールとアメリカ料理。テラス席が最高。観劇後のディナーに。',
        'address': '東京都品川区東品川2-1-3',
        'nearest_station': '天王洲アイル駅',
        'distance_note': '銀河劇場から徒歩5分',
        'opening_hours_text': '11:30〜22:00（L.O. 21:00）',
        'benefit_text': '',
        'is_featured': True,
        'featured_order': 3,
        'theaters': ['gingeki'],
    },
    {
        'name': '甘酒横丁 初音',
        'slug': 'hatsune-amazake',
        'category': '甘味処',
        'description': '甘酒横丁の甘味処。観劇後にほっと一息。名物の甘酒とみたらし団子が人気。下町情緒たっぷりの空間。',
        'address': '東京都中央区日本橋人形町1-15-6',
        'nearest_station': '人形町駅',
        'distance_note': '明治座から徒歩3分',
        'opening_hours_text': '10:00〜18:00',
        'benefit_text': '明治座チケット半券で甘酒1杯サービス',
        'is_featured': True,
        'featured_order': 4,
        'theaters': ['meijiza'],
    },
]

# ---- Coupons ----
coupons_data = [
    {
        'shop': 'cafe-de-crie-hibiya',
        'title': 'ケーキセット100円引き',
        'discount_text': '100円OFF',
        'description': '日比谷エリアの劇場チケット半券でケーキセットが100円引き',
        'conditions': '当日の半券をご提示\nケーキセットご注文時のみ',
    },
    {
        'shop': 'saizeriya-operacity',
        'title': '観劇割 全品5%OFF',
        'discount_text': '5%OFF',
        'description': '観劇チケットの半券ご提示で全品5%オフ',
        'conditions': '注文時に半券をご提示ください\n1グループ1回まで\n他割引との併用不可',
    },
    {
        'shop': 'ty-harbor',
        'title': 'クラフトビール1杯10%OFF',
        'discount_text': '10%OFF',
        'description': '銀河劇場のチケット半券でクラフトビールが10%オフ',
        'conditions': '当日の半券をご提示\nおひとり様1杯まで',
    },
    {
        'shop': 'hatsune-amazake',
        'title': '甘酒1杯サービス',
        'discount_text': '甘酒無料',
        'description': '明治座のチケット半券で甘酒1杯サービス',
        'conditions': '当日の半券をご提示\nおひとり様1杯限り',
    },
]

# ---- 実行 ----
print('=== Shop Seed Start ===')

# 既存のショップデータをクリア
Coupon.objects.all().delete()
TheaterShop.objects.all().delete()
Shop.objects.all().delete()
print('Cleared existing shop data')

for i, s in enumerate(shops_data):
    theater_slugs = s.pop('theaters')
    s['image_url'] = SHOP_IMAGES[i % len(SHOP_IMAGES)]
    shop, created = Shop.objects.update_or_create(
        slug=s['slug'],
        defaults={k: v for k, v in s.items()},
    )
    action = 'Created' if created else 'Updated'
    print(f'  {action}: {shop.name}')
    for ts in theater_slugs:
        theater = Theater.objects.filter(slug=ts).first()
        if theater:
            TheaterShop.objects.get_or_create(theater=theater, shop=shop)

print(f'\nShops: {Shop.objects.count()}')
print(f'TheaterShops: {TheaterShop.objects.count()}')

for c in coupons_data:
    shop_slug = c.pop('shop')
    shop = Shop.objects.filter(slug=shop_slug).first()
    if shop:
        coupon, created = Coupon.objects.update_or_create(
            shop=shop,
            title=c['title'],
            defaults=c,
        )
        action = 'Created' if created else 'Updated'
        print(f'  {action} coupon: {coupon.title} ({shop.name})')

print(f'\nCoupons: {Coupon.objects.count()}')
print('=== Shop Seed Done ===')
