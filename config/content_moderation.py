import re
import unicodedata


# 公開投稿で他者への攻撃として使われやすい表現に絞る。
# 作品名・あらすじなど正当な創作表現を誤判定しないよう、短い単語は登録しない。
BLOCKED_PHRASES = (
    '死ね',
    '殺してやる',
    '殺すぞ',
    'くたばれ',
    '消えろカス',
    'ゴミ人間',
    '生きる価値がない',
    'fuck you',
    'kill yourself',
    'kys',
)


def _normalize(value):
    return unicodedata.normalize('NFKC', value or '').casefold()


def find_objectionable_phrase(value):
    normalized = _normalize(value)
    compact = re.sub(r'[\W_]+', '', normalized, flags=re.UNICODE)
    for phrase in BLOCKED_PHRASES:
        normalized_phrase = _normalize(phrase)
        compact_phrase = re.sub(r'[\W_]+', '', normalized_phrase, flags=re.UNICODE)
        if normalized_phrase in normalized or compact_phrase in compact:
            return phrase
    return None
