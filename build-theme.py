#!/usr/bin/env python3
"""генератор темы silentgram.

берёт вшитую тёмную тему ayugram за основу и перекрашивает её в схему
твоих сайтов: чёрный фон, холодные серые слои, розовый единственным акцентом.

важно: в теме значения часто ссылаются на другие ключи (windowBg: lightButtonBg).
поэтому сначала раскрываем ссылки в конкретные цвета, потом красим.
иначе подмена не срабатывает и в файле остаются старые синие.
"""

import io
import re
import sys
import zipfile
from pathlib import Path

UPSTREAM = Path("/media/raid0/silentgram/upstream")
BASE_THEME = UPSTREAM / "Telegram/Resources/night.tdesktop-theme"
DEST = Path("/media/raid0/silentgram/app/themes/silentgram.tdesktop-theme")

# ── схема цветов, значения сняты с твоих сайтов ─────────────────────────
BG        = "#0a0a0c"   # фон, почти чёрный с холодным оттенком
SURFACE   = "#101016"   # первый слой
RAISED    = "#17171d"   # второй слой
HIGH      = "#1f1f27"   # самый светлый тёмный
BORDER    = "#30363d"   # бордеры
FG        = "#e6edf3"   # основной текст
SUBTEXT   = "#8b949e"   # приглушённый текст
PINK      = "#ff2e9a"   # единственный цветной акцент
DANGER    = "#e5484d"   # ошибки

HEX8 = re.compile(r"^#[0-9a-fA-F]{8}$")
HEX6 = re.compile(r"^#[0-9a-fA-F]{6}$")

# ── главные ключи задаём руками, без угадывания по правилам ────────────
OVERRIDE = {
    "windowBg": BG,
    "windowBgOver": RAISED,
    "windowBgRipple": HIGH,
    "windowFg": FG,
    "windowFgOver": FG,
    "windowBoldFg": FG,
    "windowBoldFgOver": FG,
    "windowSubTextFg": SUBTEXT,
    "windowSubTextFgOver": SUBTEXT,
    "windowFgActive": BG,
    "key": FG,
}

# ── акцентные ключи: розовый тут и только тут ──────────────────────────
ACCENT = {
    "windowActiveTextFg", "activeLineFg", "lightButtonFg",
    "checkboxCheckFg", "checkboxBorderFg", "radioButtonCheckFg",
    "sliderTrackFg", "highlightBg", "linkFg",
    "activeButtonSecondaryFg", "activeButtonSecondaryFgOver",
    "iconDefault", "notification",
    "iconActive", "iconActiveSend", "iconActiveStar",
    "checkboxCheckDisabledFg", "windowIconFg",
    "link", "subtitleTextFg", "subtitleTextFgDisabled",
    "aboutPlatformTextFg", "materialShare",
    "topicIconFg", "chatTypeActive", "reactionActiveFg",
}


def rgb(hexval):
    v = hexval.lstrip("#")
    if len(v) == 8:
        v = v[:6]
    return int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)


def luminance(hexval):
    r, g, b = rgb(hexval)
    return (r * 299 + g * 587 + b * 114) / 1000


def bluish(hexval):
    r, g, b = rgb(hexval)
    return b > r + 12 and b >= g


def pinkish(hexval):
    r, g, b = rgb(hexval)
    return r > g + 20 and b > g + 10


def parse(path):
    """список (ключ, значение, комментарий)"""
    with zipfile.ZipFile(path) as z:
        data = z.read("colors.tdesktop-theme").decode("utf-8", "replace")
    rows = []
    for line in data.splitlines():
        s = line.strip()
        if not s or ":" not in s or s.startswith("//"):
            continue
        key, rest = s.split(":", 1)
        key = key.strip()
        comment = ""
        if "//" in rest:
            rest, c = rest.split("//", 1)
            comment = "// " + c.strip()
        val = rest.strip().rstrip(";").strip()
        if key and val:
            rows.append((key, val, comment))
    return rows


def resolve(rows):
    """раскрывает ссылки ключ->ключ в конкретные цвета"""
    table = {k: v for k, v, _ in rows}
    out = {}
    for key in table:
        seen = set()
        cur = key
        val = table[key]
        while cur not in seen:
            seen.add(cur)
            if HEX6.match(val) or HEX8.match(val):
                break
            nxt = table.get(val)
            if nxt is None:
                break
            cur, val = val, nxt
        out[key] = val
    return out


def pick(key, val):
    """возвращает новый цвет для ключа"""

    # 1. главные ключи руками
    if key in OVERRIDE:
        return OVERRIDE[key]

    # 2. акцент -> розовый
    if key in ACCENT:
        return PINK

    # 3. тёмные фоны -> наши слои
    if HEX6.match(val) and luminance(val) < 90:
        if "Over" in key or "Ripple" in key or "Hover" in key:
            return RAISED
        return SURFACE

    # 4. синие/бирюзовые -> приглушённый текст,
    #    чтобы розовый остался единственным цветным
    if HEX6.match(val) and bluish(val):
        if luminance(val) < 70:
            return DANGER if "error" in key.lower() else BORDER
        return SUBTEXT

    return val


def main():
    rows = parse(BASE_THEME)
    table = resolve(rows)

    lines = [
        "// silentgram — схема сайтов shpateil.fun",
        "// чёрный фон, холодные серые слои, розовый единственным акцентом",
        "",
    ]

    used_pink = 0
    for key, _raw, comment in rows:
        val = table[key]
        new = pick(key, val)
        if new.lower() == PINK.lower():
            used_pink += 1
        tail = ("  " + comment) if comment else ""
        lines.append(f"{key}: {new};{tail}")

    colors = "\n".join(lines) + "\n"

    # проверка формата
    bad = [l for l in colors.splitlines()
           if l.strip() and not l.startswith("//") and not re.match(r"^\S+:\s*[^;]+;\s*(//.*)?$", l)]
    if bad:
        print("битые строки:", bad[:5], file=sys.stderr)
        return 1

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("colors.tdesktop-theme", colors)
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_bytes(buf.getvalue())

    # отчёт
    pink = colors.lower().count(PINK.lower())
    bg = colors.lower().count(BG.lower())
    print(f"тема: {DEST}")
    print(f"ключей: {len(rows)}, розовый: {pink}, фон: {bg}, размер: {DEST.stat().st_size} б")
    return 0


if __name__ == "__main__":
    sys.exit(main())
