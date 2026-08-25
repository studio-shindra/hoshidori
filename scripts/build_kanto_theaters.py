#!/usr/bin/env python3
"""Build the HOSHIDORI Kanto theater seed CSV from official public sources."""

import argparse
import csv
import html
import re
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen


TOKYO_SOURCE = (
    'https://www.seikatubunka.metro.tokyo.lg.jp/'
    'bunka/bunka_seisaku/0000001271'
)
SEARCH_URL = 'https://www.zenkoubun.jp/search/search.php'
DETAIL_BASE = 'https://www.zenkoubun.jp/search/'
PREFECTURES = ('神奈川県', '埼玉県', '千葉県', '茨城県', '栃木県', '群馬県')
FIELDS = (
    'name', 'slug', 'area_name', 'address', 'nearest_station',
    'description', 'website_url', 'source_url', 'prefecture', 'city',
    'google_place_id', 'is_approved', 'is_active',
)


def clean(value):
    return re.sub(r'\s+', ' ', html.unescape(value or '')).strip()


def slug_base(name):
    value = unicodedata.normalize('NFKC', name).lower()
    value = re.sub(r'[^\w\-]+', '-', value, flags=re.UNICODE).strip('-_')
    return value[:180] or 'theater'


def unique_slug(name, used):
    base = slug_base(name)
    candidate = base
    number = 2
    while candidate in used:
        candidate = f'{base[:175]}-{number}'
        number += 1
    used.add(candidate)
    return candidate


def city_from_address(address, prefecture):
    rest = address.removeprefix(prefecture)
    match = re.match(r'(.+?(?:市|区|町|村))', rest)
    return match.group(1) if match else ''


class ResultsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.href = ''
        self.cell_text = []
        self.cells = []
        self.rows = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'table' and attrs.get('id') == 'tb-list':
            self.in_table = True
        elif self.in_table and tag == 'tr':
            self.in_row = True
            self.cells = []
        elif self.in_row and tag in ('td', 'th'):
            self.in_cell = True
            self.cell_text = []
            self.href = ''
        elif self.in_cell and tag == 'a':
            self.href = attrs.get('href', '')

    def handle_data(self, data):
        if self.in_cell:
            self.cell_text.append(data)

    def handle_endtag(self, tag):
        if self.in_cell and tag in ('td', 'th'):
            self.cells.append((clean(''.join(self.cell_text)), self.href))
            self.in_cell = False
        elif self.in_row and tag == 'tr':
            if self.cells and self.cells[0][1].startswith('hall_'):
                self.rows.append(self.cells)
            self.in_row = False
        elif self.in_table and tag == 'table':
            self.in_table = False


class DetailParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_row = False
        self.in_header = False
        self.in_value = False
        self.header = []
        self.value = []
        self.link = ''
        self.data = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'tr':
            self.in_row = True
            self.header, self.value, self.link = [], [], ''
        elif self.in_row and tag == 'th':
            self.in_header = True
        elif self.in_row and tag == 'td':
            self.in_value = True
        elif self.in_value and tag == 'a' and not self.link:
            self.link = attrs.get('href', '')

    def handle_data(self, data):
        if self.in_header:
            self.header.append(data)
        elif self.in_value:
            self.value.append(data)

    def handle_endtag(self, tag):
        if tag == 'th':
            self.in_header = False
        elif tag == 'td':
            self.in_value = False
        elif tag == 'tr' and self.in_row:
            key = clean(''.join(self.header))
            value = clean(''.join(self.value))
            if key in ('名称', '所在地', '公式サイト'):
                self.data[key] = self.link if key == '公式サイト' and self.link else value
            self.in_row = False


def request_text(url, data=None):
    body = urlencode(data, doseq=True).encode() if data is not None else None
    request = Request(url, data=body, headers={'User-Agent': 'HOSHIDORI theater data importer/1.0'})
    with urlopen(request, timeout=30) as response:
        return response.read().decode('utf-8')


def search_rows(prefecture):
    base = {
        'block[]': '関東甲信越静',
        'year_area': '1900;2040',
        'pref_name': prefecture,
        'use[]': 'musical',
        'prg2': '1',
        'keyword': '',
    }
    count = int(clean(request_text(SEARCH_URL, {**base, 'status': '0', 'limit': '0'})))
    results = []
    for offset in range(0, count, 30):
        parser = ResultsParser()
        response = request_text(
            SEARCH_URL,
            {**base, 'status': '1' if offset == 0 else '2', 'limit': str(offset)},
        )
        # “もっと見る” は <tr> だけを返すため、同じパーサーで読めるよう包む。
        if offset:
            response = f'<table id="tb-list"><tbody>{response}</tbody></table>'
        parser.feed(response)
        results.extend(
            (prefecture, row[0][0], row[0][1], row[1][0] if len(row) > 1 else '')
            for row in parser.rows
        )
    return results


def fetch_detail(item):
    prefecture, fallback_name, detail_path, fallback_address = item
    detail_url = urljoin(DETAIL_BASE, detail_path)
    parser = DetailParser()
    try:
        parser.feed(request_text(detail_url))
    except Exception as error:
        print(f'warning: detail unavailable ({detail_url}): {error}')
    name = parser.data.get('名称') or fallback_name
    address = parser.data.get('所在地', '') or fallback_address
    city = city_from_address(address, prefecture)
    return {
        'name': name,
        'area_name': city,
        'address': address,
        'nearest_station': '',
        'description': '',
        'website_url': parser.data.get('公式サイト', ''),
        'source_url': detail_url,
        'prefecture': prefecture,
        'city': city,
        'google_place_id': '',
        'is_approved': 'true',
        'is_active': 'true',
    }


def tokyo_rows(path):
    rows = []
    with path.open(encoding='utf-8-sig', newline='') as handle:
        for index, row in enumerate(csv.reader(handle)):
            if index < 3 or len(row) < 43 or clean(row[1]) != '1':
                continue
            name = clean(row[2])
            if not name:
                continue
            city = clean(row[3])
            address = clean(row[4])
            if address and not address.startswith('東京都'):
                address = f'東京都{address}'
            description_parts = []
            if clean(row[11]):
                description_parts.append(f'総座席数 {clean(row[11])}席')
            if clean(row[30]):
                description_parts.append(clean(row[30]))
            rows.append({
                'name': name,
                'area_name': city,
                'address': address,
                'nearest_station': '',
                'description': '／'.join(description_parts),
                'website_url': clean(row[7]),
                'source_url': clean(row[7]) or TOKYO_SOURCE,
                'prefecture': '東京都',
                'city': city,
                'google_place_id': '',
                'is_approved': 'true',
                'is_active': 'true',
            })
    return rows


def deduplicate(rows):
    unique = {}
    for row in rows:
        key = (unicodedata.normalize('NFKC', row['name']), row['address'])
        unique.setdefault(key, row)
    return list(unique.values())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tokyo-csv', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()

    search_results = []
    with ThreadPoolExecutor(max_workers=len(PREFECTURES)) as executor:
        futures = [executor.submit(search_rows, prefecture) for prefecture in PREFECTURES]
        for future in as_completed(futures):
            search_results.extend(future.result())

    public_rows = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(fetch_detail, item) for item in search_results]
        for future in as_completed(futures):
            public_rows.append(future.result())

    rows = deduplicate(tokyo_rows(args.tokyo_csv) + public_rows)
    used = set()
    for row in sorted(rows, key=lambda item: (item['prefecture'], item['name'])):
        row['slug'] = unique_slug(row['name'], used)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda item: (item['prefecture'], item['name'])))

    by_prefecture = {}
    for row in rows:
        by_prefecture[row['prefecture']] = by_prefecture.get(row['prefecture'], 0) + 1
    print(f'wrote {len(rows)} theaters to {args.output}')
    print(' / '.join(f'{prefecture}: {count}' for prefecture, count in sorted(by_prefecture.items())))


if __name__ == '__main__':
    main()
