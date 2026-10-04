# silentgram

unofficial telegram desktop client. форк [ayugramdesktop](https://github.com/AyuGram/AyuGramDesktop),
который сам форк [telegramdesktop](https://github.com/telegramdesktop/tdesktop).

весь функционал ayugram сохранён. изменено имя, тема и поведение трея.

## что взято из ayugram

- ghost mode: не отправлять прочтения, быть офлайн скрытно, скрывать статус
- анти-реколл, локальная история удалённых и отредактированных сообщений
- несколько аккаунтов с переключением из трея
- фильтры сообщений на регулярных выражениях
- локальный премиум
- стример-режим, скриншоты сообщений
- свои шрифты, радиусы, ширина сообщений
- пересылка, перевод, свои темы оформления

## что изменено в silentgram

| что | где |
|---|---|
| имя приложения | `core/launcher.cpp`, `core/application.cpp` |
| заголовок окна | `window/main_window.cpp` |
| имя в трее и меню | `tray.cpp`, `history/history_item_helpers.cpp` |
| трей и меню macos | `platform/mac/*.mm` |
| трей без счётчика | `platform/linux/main_window_linux.cpp` |
| тема по умолчанию | `ayu/ayu_infra.cpp` |
| about и ссылки | `boxes/about_box.cpp` |

### трей без счётчика

в ayugram на линуксе счётчик непрочитанных ставится в трее безусловно —
`main_window_linux.cpp` вызывает `setBadgeNumber()` напрямую. настройка
`hideNotificationBadge` работала только на macos. в silentgram она работает везде,
по умолчанию включена, трей показывает точку.

вернуть цифры: в `tdata/ayu_settings.json` поставить `"hideNotificationBadge": false`.

### тема по умолчанию

если в папке `tdata` лежит файл `silentgram.tdesktop-theme`, клиент применяет
его при старте. тема живёт на файле и переживает перезапуск, ключ в `settingss`
не используется.

генератор темы — `build-theme.py` в корне этого репозитория.

палитра снята с сайтов shpateil.fun:

| роль | цвет |
|---|---|
| фон | `#0a0a0c` |
| слой | `#101016` |
| слой | `#17171d` |
| слой | `#1f1f27` |
| бордер | `#30363d` |
| текст | `#e6edf3` |
| приглушённый | `#8b949e` |
| акцент | `#ff2e9a` |

## сборка

нужен qt6 из системы, cmake >= 3.25, компилятор с поддержкой c++20.

```bash
git clone --recursive https://github.com/shpateil/silentgram.git
cd silentgram/Telegram
./configure.sh -D TDESKTOP_API_ID=<id> -D TDESKTOP_API_HASH=<hash>
cmake --build ../out --config Release
```

`api_id` и `api_hash` — свои. получить на
[my.telegram.org/apps](https://my.telegram.org/apps). ключи из репозитория
ayugram использовать нельзя: это официальные ключи telegram desktop, сервер
режет опубликованные ключи.

### запуск из рабочей папки

```bash
./silentgram -workdir /путь/к/папке
```

папка создаётся автоматически, основной клиент не затрагивается. удобно держать
несколько экземпляров с разными аккаунтами.

### linux desktop-файл

```
Exec=/путь/к/silentgram -workdir /путь/к/папке
StartupWMClass=silentgram
```

## лицензия

gpl-3.0 с исключением на линковку с openssl, как у telegramdesktop и ayugram.

форк обязан оставаться gpl-3.0, хранить уведомления и копирайты в каждом файле,
помечать изменения с датой и раздавать исходники. `LICENSE` и `LEGAL` не трогать.

по правилам telegram api terms нельзя использовать слово `telegram` в названии
приложения, кроме формы `unofficial telegram …`, и нельзя использовать логотип
telegram.

## кредиты

- [telegramdesktop](https://github.com/telegramdesktop/tdesktop) — основа
- [ayugramdesktop](https://github.com/AyuGram/AyuGramDesktop) — все возможности

## изменения относительно оригинала

silentgram — модифицированный форк, изменения внесены 4 октября 2026:

- переименовано имя приложения, окна, трея и меню macos
- добавлена тема по умолчанию из файла в `tdata`
- счётчик в трее на линуксе стал настраиваемым и выключен по умолчанию
- ссылки в about-боксе ведут на этот репозиторий

исходный код форка ayugramdesktop доступен под той же лицензией gpl-3.0,
см. `LICENSE` и репозиторий https://github.com/AyuGram/AyuGramDesktop
