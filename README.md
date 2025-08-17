# ITMO Programs Chatbot (AI vs AI Product)

Телеграм-бот, который помогает абитуриенту сравнить две магистерские программы ИТМО —
**«Искусственный интеллект»** и **«Управление ИИ‑продуктами (AI Product)** — и спланировать обучение.
Под капотом: web‑парсинг учебных планов, RAG-поиск по материалам программ, рекомендации элективов с учётом бэкграунда.

## Быстрый старт

1) Python 3.11+
2) `cp .env.example .env` и заполнить переменные:
```
TELEGRAM_BOT_TOKEN=...
OPENAI_API_KEY=...           # можно не заполнять при использовании локальной LLM через Ollama
EMBED_MODEL=intfloat/multilingual-e5-base
LLM_PROVIDER=openai           # openai|ollama
LLM_MODEL=gpt-4o-mini         # либо qwen2.5:7b-instruct для Ollama
```
3) `pip install -r requirements.txt`
4) Построить индекс:
```
python -m app.pipeline.build_index
```
5) Запустить бота:
```
python -m app.bot.run
```

## Что делает бот
- Отвечает **только** на вопросы по двум магистратурам ИТМО (RAG + порог релевантности).
- Сравнивает программы, формирует **советы по выбору трека** и планированию.
- Рекомендует элективы на основе анкетирования, привязывая их к учебному плану.
- Показывает ссылку на первоисточник каждого ответа.

## Архитектура
```
app/
  bot/                 # Telegram-бот (python-telegram-bot)
  core/                # RAG, промпты, гейт релевантности
  data/                # сырые и нормализованные данные
  parsers/             # парсинг страниц и учебных планов (HTML/PDF)
  pipeline/            # сборка индекса (FAISS)
```

## Источники
- Описание ИИ: https://abit.itmo.ru/program/master/ai
- Описание AI Product: https://abit.itmo.ru/program/master/ai_product
- Страница AI Talent Hub с учебным планом (PDF): https://ai.itmo.ru/ → «Изучить учебный план»

## Лицензия
MIT
