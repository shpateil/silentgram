#!/usr/bin/env python3
"""добавляет пометку о модификации в заголовок изменённых файлов.

gpl-3.0 §5(a) требует явно указать, что файл изменён, и дату изменения.
скрипт идемпотентный — повторный запуск ничего не дублирует.
"""

import sys
from pathlib import Path

NOTE = "Modified for silentgram (https://github.com/shpateil/silentgram), 2026-10-04."

ROOT = Path(__file__).parent

FILES = [
    "Telegram/SourceFiles/core/launcher.cpp",
    "Telegram/SourceFiles/core/application.cpp",
    "Telegram/SourceFiles/core/crash_report_window.cpp",
    "Telegram/SourceFiles/window/main_window.cpp",
    "Telegram/SourceFiles/tray.cpp",
    "Telegram/SourceFiles/history/history_item_helpers.cpp",
    "Telegram/SourceFiles/boxes/about_box.cpp",
    "Telegram/SourceFiles/ayu/ayu_settings.h",
    "Telegram/SourceFiles/platform/linux/tray_linux.cpp",
    "Telegram/SourceFiles/platform/linux/main_window_linux.cpp",
    "Telegram/SourceFiles/platform/mac/global_menu_mac.mm",
    "Telegram/SourceFiles/platform/mac/window_title_mac.mm",
]


def add_note(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if NOTE in text:
        return "уже есть"

    lines = text.splitlines(keepends=True)

    # блок /* ... */ в начале, если есть
    if lines and lines[0].startswith("/*"):
        end = None
        for i, line in enumerate(lines[:12], start=1):
            if "*/" in line:
                end = i
                break
        if end is not None:
            insert_at = end  # сразу после закрывающего */
            block = lines[insert_at]
            if block.rstrip().endswith("*/") and not block.rstrip().endswith("\n"):
                lines[insert_at] = block + "\n"
                insert_at += 1
            lines.insert(insert_at, NOTE + "\n")
            path.write_text("".join(lines), encoding="utf-8")
            return "добавлено"

    # однострочный комментарий
    for i, line in enumerate(lines[:14]):
        if line.lstrip().startswith("//"):
            lines.insert(i, NOTE + "\n")
            path.write_text("".join(lines), encoding="utf-8")
            return "добавлено"

    # нет шапки — ставим первой строкой
    lines.insert(0, NOTE + "\n")
    path.write_text("".join(lines), encoding="utf-8")
    return "добавлено"


def main():
    done = skipped = missing = 0
    for rel in FILES:
        p = ROOT / rel
        if not p.exists():
            print(f"НЕТ ФАЙЛА: {rel}")
            missing += 1
            continue
        r = add_note(p)
        print(f"{r:10} {rel}")
        done += 1 if r == "добавлено" else 0
        skipped += 1 if r != "добавлено" else 0
    print(f"\nобработано: {done}, уже было: {skipped}, отсутствует: {missing}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
