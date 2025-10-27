
import random
from .models import Card

def deal_cards(deck, count, reversed_enabled=True, reversed_prob=0.5, seed=''):
    rng = random.Random(seed)
    pool = list(Card.objects.filter(deck=deck).values_list('code', flat=True))
    if len(pool) < count:
        pool = [f"DEV_{i:02d}" for i in range(78)]
    rng.shuffle(pool)
    chosen = pool[:count]
    result = []
    for code in chosen:
        is_rev = reversed_enabled and (rng.random() < reversed_prob)
        result.append({'code': code, 'reversed': is_rev})
    return result
