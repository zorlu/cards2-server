from django.shortcuts import render

from server.models import Card
from app.utils import return_json

def card_list(request):
    cards = []
    """
    user_id = request.GET.get('uid')

    user = User.objects.get(pk=int(user_id))
    deck = user.decks.all().first()

    for card in deck.cards.all():
        item = card.to_json(user.id)
        cards.append(item)
    """
    for card in Card.objects.all():
        item = card.to_json()
        cards.append(item)
    return return_json({'items': cards})

def name_generator(request):
    return render(request, "namegen.html")