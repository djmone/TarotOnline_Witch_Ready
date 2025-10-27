
import requests, json
from django.conf import settings
from tarot.models import Card
from core.models import GlobalSettings

def _safe_ollama_chat(payload, base):
    try:
        # ВАЖНО: укажем stream=false явным полем
        if 'stream' not in payload:
            payload['stream'] = False

        r = requests.post(f"{base}/api/chat", json=payload, timeout=180)
        r.raise_for_status()

        data = r.json()  # теперь это один JSON-объект
        # формат /api/chat: {"message":{"role":"assistant","content":"..."}}
        if isinstance(data, dict) and 'message' in data:
            return data['message'].get('content', '')

        # запасной вариант (если вдруг вернулся массив)
        if isinstance(data, list):
            return ''.join(ch.get('message', {}).get('content', '') for ch in data)

        return ''
    except Exception as e:
        # не скрываем ошибку полностью — лог в консоль, а не "демо"
        # можно заменить print на logging
        print('[ollama/chat] error:', e)
        return ''

def _pretty_prompt(payload: dict) -> str:
    import json
    return json.dumps(payload, ensure_ascii=False, indent=2)

# --- МИСТИЧЕСКИЙ СТИЛЬ ---

def build_full_prompt(session, lang='ru'):
    preset = session.preset
    cards = session.cards_json

    sys_ru = (
        "Ты — опытный таролог в мистическом, но уважительном стиле. "
        "Твоя задача — дать вдохновляющее и образное чтение, избегая категоричных пророчеств, "
        "медицинских и финансовых советов. Пиши по-русски.\n\n"
        "СТИЛЬ: бархатный, слегка загадочный тон; метафоры как шёпот старших Арканов; "
        "никакого запугивания. Помни про свободу воли человека.\n\n"
        "ФОРМАТ (Markdown):\n"
        "## Образ расклада — краткое целостное ощущение (2–3 предложения)\n"
        "## По позициям — для каждой позиции: *Название* — **Карта (и перевёрнутость, если есть)**\n"
        "- 1–2 пункта смысла по делу\n"
        "- 1 мягкий ориентир/совет\n"
        "## Советы пути — 3–5 коротких пунктов\n"
        "## Предостережения — 2–3 аккуратных пункта без фатализма\n"
        "## Итог — 1–2 предложения-вывода (вдохновляюще, без категоричности)"
    )

    sys_en = (
        "You are an experienced tarot reader with a mystical yet respectful tone. "
        "Give evocative readings without deterministic prophecies, and no medical/financial advice. Write in English.\n\n"
        "STYLE: velvet, slightly enigmatic, gentle metaphors; never fear-mongering.\n\n"
        "FORMAT (Markdown):\n"
        "## Reading Image — a brief overall sense (2–3 sentences)\n"
        "## Positions — for each: *Title* — **Card (and reversed if so)**\n"
        "- 1–2 key meanings\n"
        "- 1 gentle guidance\n"
        "## Guidance — 3–5 short bullets\n"
        "## Warnings — 2–3 careful bullets, no fatalism\n"
        "## Closing — 1–2 sentences, uplifting, non-deterministic"
    )

    system = sys_ru if lang == 'ru' else sys_en

    # список карт кодами (как у тебя уже было)
    card_lines = []
    for it in cards:
        # инвертируем только для промпта — сейчас серверный флаг и визуал расходятся
        rev_for_prompt = not bool(it.get('reversed', False))
        try:
            card = Card.objects.get(deck=session.deck, code=it['code'])
            name = card.name_ru or card.name_en
            if rev_for_prompt:
                name += " (перевёрнутая)"
            card_lines.append(name)
        except:
            card_lines.append(it['code'] + (" (перевёрнутая)" if rev_for_prompt else ""))

    person = session.p1_name or ""
    if session.p1_dob:
        person += f" ({session.p1_dob})"
    if preset.mode == 'couple':
        p2 = session.p2_name or ""
        if session.p2_dob:
            p2 += f" ({session.p2_dob})"
        person += f" × {p2}"

    user_msg = (
      f"Preset: {preset.slug}\n"
      f"Person(s): {person}\n"
      f"Extra: {session.extra_questions}\n"
      f"Cards: {', '.join(card_lines)}\n"
      f"Positions schema: {json.dumps(preset.positions_json, ensure_ascii=False)}\n"
      f"Language: {lang}"
    )
    return system, user_msg


def build_step_prompt(session, index, lang='ru', last=False):
    preset = session.preset
    it = session.cards_json[index]

    sys_ru = (
        "Ты — таролог в мистическом стиле. Дай короткую интерпретацию ТОЛЬКО для этой карты и её позиции. "
        "Тон — бархатный, образный, без запугивания. Пиши по-русски.\n\n"
        "ФОРМАТ (2–4 предложения):\n"
        "- что это значит здесь и сейчас;\n"
        "- на что обратить внимание;\n"
        "- 1 мягкий ориентир.\n"
        "Без медицинских/финансовых советов, без категоричности."
    )

    sys_en = (
        "You are a mystical-style tarot reader. Provide a short interpretation ONLY for this card and its position. "
        "Velvety, evocative tone without fear-mongering. Write in English.\n\n"
        "FORMAT (2–4 sentences):\n"
        "- what it means here and now;\n"
        "- what to pay attention to;\n"
        "- 1 gentle guidance.\n"
        "No medical/financial advice, no determinism."
    )

    system = sys_ru if lang == 'ru' else sys_en

    pos = preset.positions_json[index] if index < len(preset.positions_json) else {'title': f'Card {index+1}'}

    person = session.p1_name or ""
    if session.p1_dob:
        person += f" ({session.p1_dob})"
    if preset.mode == 'couple':
        p2 = session.p2_name or ""
        if session.p2_dob:
            p2 += f" ({session.p2_dob})"
        person += f" × {p2}"

    tail = ""
    if last:
        tail = (
            "\n\nЗаверши одним коротким полу-шёпотом с лёгкой интригой (без угроз и категоричности), "
            "например: «Но тень ещё не сказала последнего слова…»."
            if lang == 'ru' else
            "\n\nEnd with one short, hushed line of gentle suspense (no threats), e.g., "
            "'But the shadow has not spoken its last word yet...'."
        )

    try:
        card = Card.objects.get(deck=session.deck, code=it['code'])
        card_name = card.name_ru or card.name_en
    except:
        card_name = it['code']

    if it['reversed']:
        card_name += " (перевёрнутая)"

    user_msg = (
    f"Preset: {preset.slug}; Person(s): {person}; Extra: {session.extra_questions}\n"
    f"Position: {pos}\n"
    f"Card: {card_name}{tail}"
    )
    return system, user_msg


def ask_full(session, lang='ru'):
    gs = GlobalSettings.load()
    base = gs.ollama_base_url
    model = gs.llm_model
    temperature = gs.llm_temperature
    max_tokens = gs.llm_max_tokens

    system, user_msg = build_full_prompt(session, lang=lang)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user_msg}
        ],
        "options": {"temperature": temperature, "num_ctx": max_tokens},
        "stream": False
    }
    prompt_txt = _pretty_prompt(payload)
    print("\n[LLM prompt/full]\n", prompt_txt)  # лог в консоль

    content = _safe_ollama_chat(payload, base)
    # ВОЗВРАЩАЕМ 5 значений (добавили prompt_txt)
    return model, temperature, max_tokens, content, prompt_txt



def ask_step(session, index, lang='ru'):
    gs = GlobalSettings.load()
    base = gs.ollama_base_url
    model = gs.llm_model
    temperature = gs.llm_temperature
    max_tokens = gs.llm_max_tokens

    last = (index == len(session.cards_json) - 1)
    system, user_msg = build_step_prompt(session, index, lang=lang, last=last)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user_msg}
        ],
        "options": {"temperature": temperature, "num_ctx": max_tokens},
        "stream": False
    }
    prompt_txt = _pretty_prompt(payload)
    print("\n[LLM prompt/step]\n", prompt_txt)  # лог в консоль

    content = _safe_ollama_chat(payload, base)
    # ВОЗВРАЩАЕМ 5 значений (добавили prompt_txt)
    return model, temperature, max_tokens, content, prompt_txt

