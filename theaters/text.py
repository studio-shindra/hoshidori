FULL_WIDTH_ASCII = str.maketrans(
    {chr(code): chr(code - 0xFEE0) for code in range(0xFF01, 0xFF5F)}
    | {'\u3000': ' '}
)


def normalize_theater_name(value):
    """Keep Japanese typography intact while normalizing full-width Latin text."""
    return (value or '').translate(FULL_WIDTH_ASCII).strip()
