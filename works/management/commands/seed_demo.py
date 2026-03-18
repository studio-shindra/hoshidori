from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'デモ用ダミーデータを投入（既存の作品データはクリアされます）'

    def handle(self, *args, **options):
        from accounts.models import User
        from theaters.models import Theater
        from works.models import Work, Performance, Person, PosterSubmission
        from shops.models import Shop, TheaterShop, Coupon
        from reviews.models import ViewingLog, Review

        # ---- 既存の作品関連データをクリア ----
        Review.objects.all().delete()
        ViewingLog.objects.all().delete()
        PosterSubmission.objects.all().delete()
        Performance.objects.all().delete()
        Work.objects.all().delete()
        Person.objects.all().delete()
        self.stdout.write('Cleared existing works data')

        # ---- Theaters ----
        theaters_data = [
            {'name': '新国立劇場', 'slug': 'shin-kokuritsu', 'area_name': '初台', 'address': '東京都渋谷区本町1-1-1', 'nearest_station': '京王新線 初台駅 中央口直結', 'description': '演劇・オペラ・バレエの3つの専用劇場を擁する国立の舞台芸術センター。オペラパレス・中劇場・小劇場の3ホールで構成。', 'website_url': 'https://www.nntt.jac.go.jp/'},
            {'name': '帝国劇場', 'slug': 'teikoku', 'area_name': '日比谷', 'address': '東京都千代田区丸の内3-1-1', 'nearest_station': '日比谷駅 B3出口 徒歩3分 / 有楽町駅 徒歩5分', 'description': '1911年開場の日本初の西洋式演劇劇場。東宝が運営し、ミュージカルを中心に上演。客席数約1,900席。', 'website_url': 'https://www.tohostage.com/teigeki/'},
            {'name': '東京宝塚劇場', 'slug': 'tokyo-takarazuka', 'area_name': '日比谷', 'address': '東京都千代田区有楽町1-1-3', 'nearest_station': '日比谷駅 A5出口 徒歩1分 / 有楽町駅 徒歩5分', 'description': '宝塚歌劇団の東京公演専用劇場。2,065席を有し、華やかな舞台を展開。', 'website_url': 'https://kageki.hankyu.co.jp/theater/tokyo/'},
            {'name': '日生劇場', 'slug': 'nissei', 'area_name': '日比谷', 'address': '東京都千代田区有楽町1-1-1', 'nearest_station': '日比谷駅 A13出口 徒歩1分 / 有楽町駅 徒歩5分', 'description': '1963年開場。村野藤吾設計の美しい内装で知られ、ミュージカル・オペラ・演劇を上演。客席数約1,330席。', 'website_url': 'https://www.nissaytheatre.or.jp/'},
            {'name': 'シアタークリエ', 'slug': 'theatre-crea', 'area_name': '日比谷', 'address': '東京都千代田区有楽町1-2-1', 'nearest_station': '日比谷駅 A3出口 徒歩1分 / 有楽町駅 徒歩3分', 'description': '東宝が運営するミュージカル・演劇専用劇場。客席数609席のコンパクトな空間で臨場感ある舞台を提供。', 'website_url': 'https://www.tohostage.com/theatre_crea/'},
            {'name': '明治座', 'slug': 'meijiza', 'area_name': '浜町', 'address': '東京都中央区日本橋浜町2-31-1', 'nearest_station': '都営新宿線 浜町駅 A2出口 徒歩2分', 'description': '1873年創業の伝統ある劇場。歌舞伎からミュージカル、コンサートまで幅広く上演。客席数約1,368席。', 'website_url': 'https://www.meijiza.co.jp/'},
            {'name': '東京芸術劇場', 'slug': 'tokyo-geijutsu', 'area_name': '池袋', 'address': '東京都豊島区西池袋1-8-1', 'nearest_station': 'JR・東京メトロ・西武・東武 池袋駅 西口 徒歩2分', 'description': '大ホール・プレイハウス・シアターイースト・シアターウエストの4ホールを擁する総合芸術文化施設。', 'website_url': 'https://www.geigeki.jp/'},
            {'name': 'PARCO劇場', 'slug': 'parco', 'area_name': '渋谷', 'address': '東京都渋谷区宇田川町15-1 渋谷PARCO 8F', 'nearest_station': '渋谷駅 ハチ公口 徒歩7分', 'description': '渋谷PARCOの8階に位置する636席の劇場。演劇・ミュージカルを中心に先鋭的な舞台作品を上演。', 'website_url': 'https://stage.parco.jp/'},
            {'name': '世田谷パブリックシアター', 'slug': 'setagaya-public', 'area_name': '三軒茶屋', 'address': '東京都世田谷区太子堂4-1-1 キャロットタワー内', 'nearest_station': '東急田園都市線・世田谷線 三軒茶屋駅 直結', 'description': '主劇場とシアタートラムの2ホールを擁する公共劇場。現代演劇・ダンスの創造と発信の拠点。', 'website_url': 'https://setagaya-pt.jp/'},
            {'name': '博多座', 'slug': 'hakataza', 'area_name': '中洲川端', 'address': '福岡県福岡市博多区下川端町2-1', 'nearest_station': '地下鉄空港線 中洲川端駅 7番出口直結', 'description': '九州最大級の演劇専用劇場。歌舞伎・ミュージカル・演劇など多彩な演目を上演。客席数約1,500席。', 'website_url': 'https://www.hakataza.co.jp/'},
            {'name': '梅田芸術劇場', 'slug': 'umeda-geijutsu', 'area_name': '梅田', 'address': '大阪府大阪市北区茶屋町19-1', 'nearest_station': '阪急 大阪梅田駅 茶屋町口 徒歩3分', 'description': 'メインホール（1,905席）とシアター・ドラマシティ（898席）の2ホールを擁する西日本最大級の劇場。', 'website_url': 'https://www.umegei.com/'},
            {'name': '御園座', 'slug': 'misonoza', 'area_name': '伏見', 'address': '愛知県名古屋市中区栄1-6-14', 'nearest_station': '地下鉄東山線・鶴舞線 伏見駅 1番出口 徒歩2分', 'description': '1896年創業の名古屋を代表する劇場。2018年リニューアル。歌舞伎・ミュージカルを中心に上演。客席数約1,300席。', 'website_url': 'https://www.misonoza.co.jp/'},
            {'name': 'シアターオーブ', 'slug': 'theatre-orb', 'area_name': '渋谷', 'address': '東京都渋谷区神南2-21-1 渋谷ヒカリエ 11F', 'nearest_station': '渋谷駅 東口・宮益坂口 徒歩5分（ヒカリエ直結）', 'description': '渋谷ヒカリエ11階に位置する約1,972席の劇場。海外ミュージカルの来日公演を中心に上演。', 'website_url': 'https://theatre-orb.com/'},
            {'name': '紀伊國屋ホール', 'slug': 'kinokuniya', 'area_name': '新宿', 'address': '東京都新宿区新宿3-17-7 紀伊國屋書店新宿本店4F', 'nearest_station': 'JR新宿駅 東口 徒歩5分', 'description': '紀伊國屋書店新宿本店4階にある客席数418席の劇場。1964年開場以来、数々の名作を生み出した演劇の殿堂。', 'website_url': 'https://www.kinokuniya.co.jp/contents/kinokuniya-hall/'},
            {'name': '本多劇場', 'slug': 'honda', 'area_name': '下北沢', 'address': '東京都世田谷区北沢2-10-15', 'nearest_station': '小田急線・京王井の頭線 下北沢駅 南口 徒歩2分', 'description': '1982年開場。下北沢の演劇文化を象徴する386席の劇場。小劇場演劇の聖地として知られる。', 'website_url': 'http://www.honda-geki.com/'},
            {'name': 'サンシャイン劇場', 'slug': 'sunshine', 'area_name': '池袋', 'address': '東京都豊島区東池袋3-1-4 サンシャインシティ文化会館4F', 'nearest_station': '東京メトロ有楽町線 東池袋駅 6・7番出口 徒歩3分', 'description': 'サンシャインシティ内にある客席数約808席の劇場。演劇・ミュージカル・2.5次元舞台を中心に上演。', 'website_url': 'https://sunshine-theatre.co.jp/'},
            {'name': '銀河劇場', 'slug': 'gingeki', 'area_name': '天王洲', 'address': '東京都品川区東品川2-3-16 シーフォートスクエア2F', 'nearest_station': 'りんかい線 天王洲アイル駅 B出口 徒歩1分 / 東京モノレール 天王洲アイル駅 徒歩5分', 'description': '天王洲アイルに位置する客席数746席の劇場。ミュージカル・2.5次元舞台を中心に上演。', 'website_url': 'https://www.gingeki.jp/'},
            {'name': 'シアター1010', 'slug': 'theater-1010', 'area_name': '北千住', 'address': '東京都足立区千住3-92 千住ミルディスⅠ番館 10F・11F', 'nearest_station': 'JR・東京メトロ・東武・つくばエクスプレス 北千住駅 西口 徒歩2分', 'description': '北千住マルイ上層階にある公共ホール。大ホール（701席）と小ホールを併設。演劇・音楽・ダンスなど多目的に使用。', 'website_url': 'https://www.t1010.jp/'},
            {'name': '宝塚大劇場', 'slug': 'takarazuka-daigekijo', 'area_name': '宝塚', 'address': '兵庫県宝塚市栄町1-1-57', 'nearest_station': '阪急宝塚線 宝塚駅 徒歩10分 / JR宝塚線 宝塚駅 徒歩10分', 'description': '宝塚歌劇団の本拠地。2,550席を有する大劇場で、花・月・雪・星・宙の5組が公演。', 'website_url': 'https://kageki.hankyu.co.jp/theater/takarazuka/'},
            {'name': '森ノ宮ピロティホール', 'slug': 'morinomiya-piloti', 'area_name': '森ノ宮', 'address': '大阪府大阪市中央区森ノ宮中央1-17-5', 'nearest_station': 'JR環状線・地下鉄中央線 森ノ宮駅 徒歩3分', 'description': '大阪城公園に隣接する多目的ホール。客席数約1,030席。演劇・コンサート・イベントに幅広く使用。', 'website_url': 'https://www.piloti-hall.jp/'},
        ]
        for t in theaters_data:
            obj, created = Theater.objects.get_or_create(slug=t['slug'], defaults=t)
            if not created:
                for key, val in t.items():
                    if key != 'slug':
                        setattr(obj, key, val)
                obj.save()
        self.stdout.write(f'Theaters: {Theater.objects.count()}')

        # ---- Works + Performances ----
        admin_user = User.objects.filter(is_superuser=True).first()
        works_data = [
            {'title': '星降る夜のワルツ', 'theater': 'shin-kokuritsu', 'start': '2026-04-01', 'end': '2026-04-30'},
            {'title': 'ガラスの迷宮', 'theater': 'teikoku', 'start': '2026-04-05', 'end': '2026-06-30'},
            {'title': 'さよならの先へ', 'theater': 'teikoku', 'start': '2026-07-01', 'end': '2026-08-31'},
            {'title': '月曜日のピエロ', 'theater': 'tokyo-takarazuka', 'start': '2026-03-15', 'end': '2026-04-15'},
            {'title': '約束の庭', 'theater': 'morinomiya-piloti', 'start': '2026-05-01', 'end': '2026-05-31'},
            {'title': '嵐のあとで', 'theater': 'theatre-orb', 'start': '2026-06-01', 'end': '2026-07-31'},
            {'title': '夜明けのレッスン', 'theater': 'sunshine', 'start': '2026-03-01', 'end': '2026-12-31'},
            {'title': '水色の手紙', 'theater': 'tokyo-geijutsu', 'start': '2026-05-10', 'end': '2026-06-10'},
            {'title': '花と嘘と秘密', 'theater': 'teikoku', 'start': '2026-09-01', 'end': '2026-10-31'},
            {'title': '路地裏のセレナーデ', 'theater': 'teikoku', 'start': '2026-11-01', 'end': '2026-12-31'},
            {'title': '雨の日の天使', 'theater': 'theatre-crea', 'start': '2026-04-10', 'end': '2026-05-10'},
            {'title': '銀色のカーテンコール', 'theater': 'tokyo-takarazuka', 'start': '2026-05-01', 'end': '2026-06-15'},
            {'title': '虹を渡る人', 'theater': 'nissei', 'start': '2026-06-01', 'end': '2026-07-15'},
            {'title': '風の忘れもの', 'theater': 'umeda-geijutsu', 'start': '2026-04-01', 'end': '2026-05-15'},
            {'title': '真夜中の図書館', 'theater': 'meijiza', 'start': '2026-03-20', 'end': '2026-04-20'},
            {'title': '時をかける旅人', 'theater': 'parco', 'start': '2026-03-01', 'end': '2026-12-31'},
            {'title': '黄昏のダンスホール', 'theater': 'setagaya-public', 'start': '2026-05-01', 'end': '2026-05-31'},
            {'title': '海辺の椅子', 'theater': 'hakataza', 'start': '2026-06-01', 'end': '2026-06-30'},
            {'title': '鏡の中の街', 'theater': 'teikoku', 'start': '2026-03-01', 'end': '2026-03-31'},
            {'title': '窓辺のアリア', 'theater': 'misonoza', 'start': '2026-07-01', 'end': '2026-07-31'},
        ]
        for w in works_data:
            work, _ = Work.objects.get_or_create(
                title=w['title'],
                defaults={'created_by': admin_user}
            )
            theater = Theater.objects.filter(slug=w['theater']).first()
            if theater:
                Performance.objects.get_or_create(
                    work=work, theater=theater,
                    defaults={
                        'start_date': w['start'], 'end_date': w['end'],
                        'created_by': admin_user,
                    }
                )
        self.stdout.write(f'Works: {Work.objects.count()}, Performances: {Performance.objects.count()}')

        # ---- Shops ----
        shops_data = [
            {'name': 'Paul 新宿南口店', 'slug': 'paul-shinjuku', 'category': 'カフェ・ベーカリー', 'address': '東京都渋谷区代々木2-7-7', 'nearest_station': '新宿駅', 'distance_note': '新国立劇場から徒歩8分', 'theaters': ['shin-kokuritsu']},
            {'name': 'タリーズコーヒー 初台店', 'slug': 'tullys-hatsudai', 'category': 'カフェ', 'address': '東京都渋谷区初台1-9-1', 'nearest_station': '初台駅', 'distance_note': '新国立劇場から徒歩2分', 'theaters': ['shin-kokuritsu']},
            {'name': '鳥貴族 初台店', 'slug': 'torikizoku-hatsudai', 'category': '居酒屋', 'address': '東京都渋谷区初台1-12-5', 'nearest_station': '初台駅', 'distance_note': '新国立劇場から徒歩3分', 'theaters': ['shin-kokuritsu']},
            {'name': 'サイゼリヤ オペラシティ店', 'slug': 'saizeriya-operacity', 'category': 'レストラン', 'address': '東京都新宿区西新宿3-20-2', 'nearest_station': '初台駅', 'distance_note': '新国立劇場直結', 'theaters': ['shin-kokuritsu']},
            {'name': 'ドトールコーヒー 初台店', 'slug': 'doutor-hatsudai', 'category': 'カフェ', 'address': '東京都新宿区西新宿3-20-2 B1F', 'nearest_station': '初台駅', 'distance_note': '新国立劇場直結', 'theaters': ['shin-kokuritsu']},
            {'name': 'カフェ・ド・クリエ 日比谷店', 'slug': 'cafe-de-crie-hibiya', 'category': 'カフェ', 'address': '東京都千代田区有楽町1-2-2', 'nearest_station': '日比谷駅', 'distance_note': '帝国劇場から徒歩2分', 'theaters': ['teikoku', 'nissei', 'theatre-crea', 'tokyo-takarazuka']},
            {'name': 'ペニンシュラ東京 ザ・ロビー', 'slug': 'peninsula-lobby', 'category': 'ラウンジ', 'address': '東京都千代田区有楽町1-8-1', 'nearest_station': '日比谷駅', 'distance_note': '帝国劇場から徒歩3分', 'theaters': ['teikoku', 'nissei']},
            {'name': 'ビヤホール ライオン 銀座七丁目店', 'slug': 'lion-ginza', 'category': 'ビアホール', 'address': '東京都中央区銀座7-9-20', 'nearest_station': '銀座駅', 'distance_note': '帝国劇場から徒歩10分', 'theaters': ['teikoku']},
            {'name': 'スターバックス 池袋西口店', 'slug': 'starbucks-ikebukuro', 'category': 'カフェ', 'address': '東京都豊島区西池袋1-1-25', 'nearest_station': '池袋駅', 'distance_note': '東京芸術劇場から徒歩1分', 'theaters': ['tokyo-geijutsu', 'sunshine']},
            {'name': 'サクラカフェ 池袋', 'slug': 'sakura-cafe-ikebukuro', 'category': 'カフェ・レストラン', 'address': '東京都豊島区池袋2-39-10', 'nearest_station': '池袋駅', 'distance_note': '東京芸術劇場から徒歩5分', 'theaters': ['tokyo-geijutsu']},
            {'name': 'ヴィレッジヴァンガード ダイナー 下北沢', 'slug': 'vv-diner-shimokita', 'category': 'ダイナー', 'address': '東京都世田谷区北沢2-26-15', 'nearest_station': '下北沢駅', 'distance_note': '本多劇場から徒歩3分', 'theaters': ['honda']},
            {'name': '珈琲館 渋谷店', 'slug': 'kohikan-shibuya', 'category': 'カフェ', 'address': '東京都渋谷区宇田川町15-1', 'nearest_station': '渋谷駅', 'distance_note': 'PARCO劇場から徒歩1分', 'theaters': ['parco', 'theatre-orb']},
        ]
        for s in shops_data:
            theater_slugs = s.pop('theaters')
            shop, _ = Shop.objects.get_or_create(slug=s['slug'], defaults=s)
            for ts in theater_slugs:
                theater = Theater.objects.filter(slug=ts).first()
                if theater:
                    TheaterShop.objects.get_or_create(theater=theater, shop=shop)
        self.stdout.write(f'Shops: {Shop.objects.count()}, TheaterShops: {TheaterShop.objects.count()}')

        # ---- Coupons ----
        coupons_data = [
            {'shop': 'saizeriya-operacity', 'title': '観劇割 全品5%OFF', 'discount_text': '全品5%OFF', 'description': '観劇チケットの半券ご提示で割引', 'conditions': '注文時に半券をご提示ください\n1グループ1回まで'},
            {'shop': 'tullys-hatsudai', 'title': 'ドリンク50円引き', 'discount_text': '50円OFF', 'description': '観劇チケット提示でドリンク割引', 'conditions': 'チケット半券ご提示'},
            {'shop': 'cafe-de-crie-hibiya', 'title': 'ケーキセット100円引き', 'discount_text': '100円OFF', 'description': '日比谷エリアの劇場チケット半券で割引', 'conditions': '当日の半券をご提示'},
            {'shop': 'sakura-cafe-ikebukuro', 'title': 'ランチ10%OFF', 'discount_text': '10%OFF', 'description': '池袋エリアの劇場チケットで割引', 'conditions': '当日の半券をご提示\nランチタイム限定'},
        ]
        for c in coupons_data:
            shop = Shop.objects.filter(slug=c.pop('shop')).first()
            if shop:
                Coupon.objects.get_or_create(shop=shop, title=c['title'], defaults=c)
        self.stdout.write(f'Coupons: {Coupon.objects.count()}')

        # ---- Posters ----
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
                user=admin_user,
                defaults={
                    'image_url': url,
                    'image_public_id': public_id,
                    'image_width': 600,
                    'image_height': 900,
                    'image_format': 'png',
                    'is_selected': True,
                },
            )
        self.stdout.write(f'Posters: {PosterSubmission.objects.count()}')

        self.stdout.write(self.style.SUCCESS('Done!'))
