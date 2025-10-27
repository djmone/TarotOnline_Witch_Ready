
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.utils.timezone import now
from core.utils_fairness import make_seed, commit_seed
from core.models import GlobalSettings
from accounts.models import Profile
from .models import Deck, Card, SpreadPreset, SpreadSession, SpreadReading
from .services_shuffle import deal_cards
from .services_llm import ask_full, ask_step
import math

def home(request):
    presets = SpreadPreset.objects.all().order_by('id')
    return render(request, 'tarot/home.html', {'presets': presets})

@login_required
def start_form(request):
    presets = SpreadPreset.objects.all().order_by('id')
    return render(request,'tarot/start_form.html',{'presets':presets})

@login_required
def start_session(request, preset_slug):
    preset = get_object_or_404(SpreadPreset, slug=preset_slug)
    if request.method != 'POST':
        return render(request, 'tarot/start_simple.html', {'preset':preset})
    gs = GlobalSettings.load()
    deck = Deck.objects.first()
    prof = request.user.profile
    price = preset.price_credits
    if prof.free_uses_remaining <= 0 and prof.credits < price:
        return render(request,'tarot/no_credits.html',{'need':price})
    p1_name = request.POST.get('p1_name') or 'Клиент'
    p1_dob  = request.POST.get('p1_dob') or None
    p2_name = request.POST.get('p2_name','')
    p2_dob  = request.POST.get('p2_dob') or None
    extra   = request.POST.get('extra_questions','')
    reveal_mode = request.POST.get('reveal_mode','all')
    seed = make_seed()
    created_iso = now().isoformat()
    shash = commit_seed(seed, request.user.id, preset.slug, created_iso)
    session = SpreadSession.objects.create(
        user=request.user, preset=preset, deck=deck,
        seed=seed, seed_hash=shash,
        reversed_enabled=gs.reversed_enabled, reversed_prob=gs.reversed_prob,
        p1_name=p1_name, p1_dob=p1_dob, p2_name=p2_name, p2_dob=p2_dob,
        extra_questions=extra, reveal_mode=reveal_mode
    )
    if prof.free_uses_remaining > 0: prof.free_uses_remaining -= 1
    else: prof.credits -= price
    prof.save()
    return render(request,'tarot/session_animate.html',{'session':session,'preset':preset})

@login_required
def deal_api(request, session_id):
    session = get_object_or_404(SpreadSession, pk=session_id, user=request.user)
    if session.cards_json:
        return JsonResponse(session.cards_json, safe=False)
    picked = deal_cards(session.deck, session.preset.cards_count,
                        reversed_enabled=session.reversed_enabled,
                        reversed_prob=session.reversed_prob,
                        seed=session.seed)
    cards_info = []
    R = 40.0
    n = session.preset.cards_count
    for i, it in enumerate(picked):
        ang = math.pi*0.6 + i*(math.pi*0.8/max(1,n-1))
        x = R*math.cos(ang)
        z = R*math.sin(ang)
        try:
            card = Card.objects.get(deck=session.deck, code=it['code'])
            url = card.img_upright.url if card.img_upright else '/static/tarot/img/placeholder.jpg'
        except Card.DoesNotExist:
            url = '/static/tarot/img/placeholder.jpg'
        cards_info.append({'code': it['code'], 'img_url': url, 'x': x, 'z': z, 'reversed': it['reversed']})
    session.cards_json = cards_info
    session.save(update_fields=['cards_json'])
    return JsonResponse(cards_info, safe=False)

@login_required
def interpret_full(request, session_id):
    session = get_object_or_404(SpreadSession, pk=session_id, user=request.user)
    model, temp, ctx, text, prompt = ask_full(session, lang='ru')
    SpreadReading.objects.update_or_create(session=session, defaults={
        'model': model, 'temperature': temp, 'tokens': ctx, 'response_text': text, 'prompt_used':'full'
    })
    return render(request, 'tarot/session_result.html', {
        'session': session,
        'reading': text,
        'prompt': prompt,          # ← добавили
    })

@login_required
def interpret_step(request, session_id):
    session = get_object_or_404(SpreadSession, pk=session_id, user=request.user)
    try:
        idx = int(request.GET.get('index','0'))
    except:
        return HttpResponseBadRequest("bad index")
    if idx<0 or idx>=len(session.cards_json):
        return HttpResponseBadRequest("out of range")
    model, temp, ctx, text = ask_step(session, idx, lang='ru')
    return JsonResponse({'index': idx, 'text': text})

@login_required
def export_pdf(request, session_id):
    return HttpResponse("PDF export placeholder", content_type="text/plain")
