# api/management/commands/seed_works_from_list.py

import json
import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone

from api.models import Work, Theater, Actor, Run

from openai import OpenAI


class Command(BaseCommand):
    help = "Seed HOSHIDORI Works (and related Theaters/Actors/Runs) from WORKS_DATA, optionally fetched from OpenAI."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without writing to the DB",
        )
        parser.add_argument(
            "--year",
            type=int,
            help="対象年 (OpenAIから作品リストを取ってくるときに使う)",
        )
        parser.add_argument(
            "--month",
            type=int,
            help="対象月 (OpenAIから作品リストを取ってくるときに使う, 1-12)",
        )
        parser.add_argument(
            "--use-openai",
            action="store_true",
            help="WORKS_DATA を OpenAI ChatCompletion 経由で生成してから投入する",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        year = options.get("year")
        month = options.get("month")
        use_openai = options["use_openai"]

        # 年月が指定されていなければ、「今月」をデフォルトにする
        today = timezone.localdate()
        if year is None:
            year = today.year
        if month is None:
            month = today.month

        if use_openai:
            self.stdout.write(self.style.SUCCESS(f"Fetching WORKS_DATA from OpenAI for {year}-{month:02d} ..."))
            works_data = self._fetch_works_from_openai(year, month)
            self.stdout.write(self.style.SUCCESS(f"Received {len(works_data)} works from OpenAI."))
        else:
            self.stdout.write(self.style.WARNING("use-openai が指定されていないため、WORKS_DATA は空になります。"))
            works_data = []

        self.stdout.write(self.style.SUCCESS("Starting seeding works..."))
        for data in works_data:
            self._process_work(data, dry_run=dry_run)
        self.stdout.write(self.style.SUCCESS("Done."))

    # ==========================
    # OpenAI から WORKS_DATA を取得
    # ==========================

    def _fetch_works_from_openai(self, year: int, month: int):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY が環境変数に設定されていません。")

        # v1 クライアントを生成（環境変数 OPENAI_API_KEY を自動で読む）
        client = OpenAI(api_key=api_key)

        ym = f"{year}年{month}月"

        system_prompt = (
            "あなたは観劇ログアプリ「HOSHIDORI v2」用の作品データを作るアシスタントです。"
            "日本の舞台作品についての一般的な知識を元に、指定された年月・エリアに合いそうな作品候補を提案してください。"
            "結果は JSON 形式で返してください。"
        )

        user_prompt = f"""
    以下の条件で、JSON オブジェクトを返してください。

    # 条件

    - 対象期間：
    - {ym}
    - 対象エリア：
    - 日本・東京で上演された舞台作品
    - 対象ジャンル：
    - 演劇、小劇場、大劇場、ミュージカル、2.5次元を含む「舞台公演」
    - ライブ、コンサート、イベント系は除外
    - 本数：
    - 15本前後（厳密でなくてよい）

    # 出力フォーマット（重要）

    次のような JSON オブジェクトを返してください:

    {{
    "works": [
        {{
        "title": "作品タイトル",          # 日本語
        "slug": "slug-identifier",        # 英数字とハイフンのみ
        "troupe": "劇団名 or 主催名",
        "main_theater": "劇場名",
        "actors": ["俳優A", "俳優B"],
        "tags": ["会話劇", "2.5次元"],
        "status": "APPROVED",
        "image_url": "",
        "runs": [
            {{
            "label": "東京公演",
            "area": "東京",
            "theater": "劇場名",
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
            }}
        ]
        }}
    ]
    }}

    - 画像URL（ポスター画像など）は、正確な公式URLが分からなければ必ず空文字にしてください。
    - 日付や劇団名などが不明な場合は、無理に埋めずに null や空文字を使って構いません。
    """

        resp = client.chat.completions.create(
            model="gpt-4o-mini",  # ここは使いたいモデル名に合わせる
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )

        content = resp.choices[0].message.content
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR("OpenAI からの応答を JSON としてパースできませんでした。"))
            self.stdout.write(content)
            raise

        works = parsed.get("works") or []
        if not isinstance(works, list):
            self.stdout.write(self.style.ERROR("JSON の 'works' がリストではありません。"))
            raise RuntimeError("Invalid JSON format from OpenAI")

        cleaned = []
        for w in works:
            if isinstance(w, dict):
                cleaned.append(w)
        return cleaned

    # ==========================
    # Theater ヘルパー
    # ==========================

    def _get_or_create_theater(self, name: str, dry_run: bool = False):
        name = name.strip()
        if not name:
            return None

        if dry_run:
            self.stdout.write(f"[DRY RUN] Theater: {name}")
            return None

        qs = Theater.objects.filter(name=name)
        if qs.exists():
            theater = qs.first()
            if qs.count() > 1:
                self.stdout.write(
                    self.style.WARNING(
                        f"[WARN] Multiple theaters named '{name}' found. Using id={theater.id}."
                    )
                )
        else:
            theater = Theater.objects.create(name=name)
            self.stdout.write(self.style.SUCCESS(f"Created Theater: {theater.name}"))

        return theater

    # ==========================
    # Work / Actor / Run の投入
    # ==========================

    def _process_work(self, data: dict, dry_run: bool = False):
        title = (data.get("title") or "").strip()
        if not title:
            return

        slug = (data.get("slug") or slugify(title)).strip()
        troupe = (data.get("troupe") or "").strip()
        main_theater_name = (data.get("main_theater") or "").strip()
        actor_names = data.get("actors") or []
        tags = data.get("tags") or []
        status = data.get("status") or "DRAFT"
        image_url = (data.get("image_url") or "").strip()

        # Theater
        main_theater = None
        if main_theater_name:
            main_theater = self._get_or_create_theater(main_theater_name, dry_run=dry_run)

        # Work
        if dry_run:
            self.stdout.write(f"[DRY RUN] Work: {title} (slug={slug})")
            return

        work, created = Work.objects.get_or_create(
            slug=slug,
            defaults={
                "title": title,
                "troupe": troupe,
                "main_theater": main_theater,
                "status": status,
            },
        )
        if not created:
            work.title = title
            work.troupe = troupe
            work.main_theater = main_theater
            work.status = status

        # 画像URLは main_image_url に入れておく（Cloudinaryへの自動再アップは行わない）
        if image_url:
            work.main_image_url = image_url

        work.save()
        self.stdout.write(
            self.style.SUCCESS(
                f"{'Created' if created else 'Updated'} Work: {work} (slug={slug})"
            )
        )

        # Actors
        for name in actor_names:
            name = (name or "").strip()
            if not name:
                continue
            actor, _ = Actor.objects.get_or_create(name=name)
            work.actors.add(actor)

        # tags
        if tags:
            work.tags.set(tags)

        # Runs
        runs = data.get("runs") or []
        for r in runs:
            if not isinstance(r, dict):
                continue
            label = (r.get("label") or "").strip() or "公演"
            area = (r.get("area") or "").strip()
            theater_name = (r.get("theater") or main_theater_name).strip()
            start_date = r.get("start_date") or None
            end_date = r.get("end_date") or None

            theater_obj = None
            if theater_name:
                theater_obj = self._get_or_create_theater(theater_name, dry_run=False)

            run, _ = Run.objects.get_or_create(
                work=work,
                label=label,
                defaults={
                    "area": area,
                    "theater": theater_obj,
                    "start_date": start_date,
                    "end_date": end_date,
                },
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"  Run: {run.label} ({run.start_date}〜{run.end_date})"
                )
            )