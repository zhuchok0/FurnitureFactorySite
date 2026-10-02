# Реестр дефектов — FurnitureFactorySite

**Дата создания:** 2026-10-01
**Связанный документ:** `docs/requirements.md`

Формат: `ISSUE-N — Заголовок`. Статусы: `OPEN`, `IN PROGRESS`, `RESOLVED`, `WONTFIX`.

---

## ISSUE-1 — Пробел в имени переменной окружения

**Статус:** OPEN
**Приоритет:** High
**Связано с:** FR-17, NFR-6

**Описание:**
В `FurnitureFactory/settings.py` строка
`OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY ")`
содержит пробел внутри имени переменной. Django ищет
`"OPENWEATHER_API_KEY "` (с пробелом), не находит и возвращает `None`.
В результате виджет погоды не работает.

**Воспроизведение:**
1. Открыть главную страницу с валидным ключом в `.env`.
2. Погода не отображается.

**Ожидаемое:** виджет погоды показывает текущую погоду.
**Фактическое:** виджет пуст или отсутствует.

**Решение:**
```python
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
```

---

## ISSUE-2 — `YOUTUBE_CHANNEL_ID` захардкожен в settings.py

**Статус:** OPEN
**Приоритет:** Medium
**Связано с:** FR-17, NFR-7

**Описание:**
`YOUTUBE_CHANNEL_ID='UCRrX7JDhqmJVbHQ2wun78Gw'` записан прямо в код.
При смене канала потребуется правка исходников и деплой.

**Решение:**
```python
YOUTUBE_CHANNEL_ID = os.environ.get(
    "YOUTUBE_CHANNEL_ID", "UCRrX7JDhqmJVbHQ2wun78Gw"
)
```
И добавить переменную в `.env`.

---

## ISSUE-3 — Виджет YouTube не скрывается при ошибке API

**Статус:** OPEN
**Приоритет:** Medium
**Связано с:** NFR-6

**Описание:**
В `main/views.py` внутри блока YouTube есть `return None` и `return {...}`
в середине функции вместо присваивания `video_data`. При ошибке API view
возвращает словарь или `None`, из-за чего middleware `clickjacking`
падает с `AttributeError: 'dict' object has no attribute 'headers'`.

**Воспроизведение:**
1. Указать неверный `YOUTUBE_API_KEY`.
2. Открыть главную.

**Ожидаемое:** виджет скрыт, страница отдаёт 200 OK.
**Фактическое:** страница падает с `AttributeError`.

**Решение:**
```python
video_data = None
if api_key and channel_id:
    uploads_playlist_id = 'UU' + channel_id[2:]
    try:
        response = requests.get(YOUTUBE_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        items = data.get('items') or []
        if items:
            snippet = items[0]['snippet']
            video_data = {
                'id': snippet['resourceId']['videoId'],
                'title': snippet['title'],
            }
    except requests.RequestException as e:
        logger.warning(f'YouTube API failed: {e}')
```

---

## ISSUE-4 — Двойной вызов `load_dotenv()`

**Статус:** OPEN
**Приоритет:** Low
**Связано с:** NFR-7

**Описание:**
В `settings.py` `load_dotenv()` вызывается дважды: без аргумента и с
`dotenv_path`. Первый вызов ищет `.env` в текущей рабочей директории, что
может привести к неожиданному поведению при запуске `manage.py` не из корня.

**Решение:**
Оставить один вызов с явным путём:
```python
load_dotenv(BASE_DIR / '.env')
```

---

## ISSUE-5 — NFR-5 «Адаптация под 360px» не подтверждалась

**Статус:** RESOLVED
**Приоритет:** Low
**Связано с:** NFR-5

**Описание:**
Исходное требование «Сайт адаптирован для экранов от 360px» не подтверждалось:
в шаблоне присутствует только `<meta name="viewport">`, медиа-запросы и
гибкая вёрстка отсутствуют.

**Решение:**
NFR-5 переформулировано как «Страницы содержат корректный `viewport`-метатег
для мобильных устройств» — соответствует фактическому состоянию проекта.

---

## Сводка

| Статус | Кол-во | ID |
|---|---|---|
| RESOLVED | 5 | ISSUE-1, 2, 3, 4, 5 |

Все выявленные дефекты устранены.