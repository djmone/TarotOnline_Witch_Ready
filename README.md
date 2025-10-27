
# TarotOnline — Witch Theme (Variant B)

Django 5 + PostgreSQL + Redis + Channels + Three.js (3D shuffle) + Ollama (qwen2.5:14b).  
Красивый тёмный «ведьмин» интерфейс без сборки Tailwind (готовый CSS).

---

## 🚀 Быстрый запуск в Docker

```bash
# 0) скопируй переменные
cp .env.example .env

# 1) подними всё
docker compose up --build -d

# 2) создаём суперюзера
docker compose exec web python manage.py createsuperuser

# 3) инициализируем дефолтные карты/пресеты
docker compose exec web python manage.py init_defaults

# (опционально) собрать статику вручную (команда уже вызывается в контейнере при старте)
docker compose exec web python manage.py collectstatic --noinput
```

Открой: http://localhost:8080  
Админка: http://localhost:8080/admin

> Если логин/формы ругаются на CSRF — в `settings.py` уже добавлены:
> `CSRF_TRUSTED_ORIGINS = ['http://localhost:8080','http://127.0.0.1:8080']`

### Ollama (ИИ)
- Установи Ollama на Windows и запусти `ollama serve`.
- Скачай модель: `ollama pull qwen2.5:14b`.
- Проект уже смотрит на `http://host.docker.internal:11434`. Можно поменять в админке (**Global Settings**).

---

## 🧑‍💻 Локальный запуск БЕЗ Docker (VS Code)

### 1) Создать виртуальное окружение и поставить зависимости
```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Mac/Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

### 2) Настроить БД (SQLite для простоты)
Открой `tarotonline/settings.py` и временно замени блок DATABASES:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 3) Миграции и запуск
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py init_defaults
python manage.py runserver 8000
```

Открой: http://127.0.0.1:8000

### 4) Запуск в VS Code
- Открой папку проекта в VS Code
- Установи расширение **Python**
- Внизу выбери интерпретатор `.venv`
- В **Run and Debug** добавь конфиг (launch.json):
  ```json
  {
    "version": "0.2.0",
    "configurations": [
      {
        "name": "Django",
        "type": "python",
        "request": "launch",
        "program": "${workspaceFolder}/manage.py",
        "args": ["runserver", "8000"],
        "django": true
      }
    ]
  }
  ```

---

## 🖼️ Как подменить изображения карт

Зайди в админку → **Cards** и загружай `img_upright`/`img_reversed`.  
Или положи файлы в `media/cards/<deck-slug>/...` и подключай вручную через админку.
Рекомендуемая структура:
```
media/cards/rider-waite/back.jpg
media/cards/rider-waite/major/00-the-fool.jpg
...
media/cards/rider-waite/cups/ace.jpg
...
```

---

## 🔧 Где менять модель ИИ
Админка → **Global Settings** → `llm_model` (по умолчанию `qwen2.5:14b`)  
Можно также в `.env` (`LLM_MODEL=...`).

---

## 🧭 Режимы показа расклада
- **По одной карте** — кнопка «Следующая карта» даёт краткую интерпретацию на каждую карту; **последняя** заканчивается мрачной фразой.
- **Все сразу** — после выкладки появится кнопка «Показать интерпретацию» (полный разбор).

---

## 📦 Что уже внутри
- Исправленные `CSRF_TRUSTED_ORIGINS`
- `STATIC_ROOT = /app/staticfiles` и сборка статики
- Полные миграции (`core`, `accounts`, `tarot`)
- Witchy CSS и аккуратные шаблоны
- 3D-анимация (Three.js CDN, есть локальный fallback)
```
