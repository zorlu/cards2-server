from django.core.management.base import BaseCommand
from server.models import Card, Deck
from random import randint

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


my_mana_map = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
mana_map = {
    1: 7,
    2: 6,
    3: 6,
    4: 5,
    5: 3,
    6: 2,
    7: 1
}

spell_cards = []
creature_cards = []
spell_count = 6
creature_count = 24


class Command(BaseCommand):
    def handle(self, *args, **options):
        user_id = 2

        browser = webdriver.PhantomJS()
        browser.implicitly_wait(30)

        browser.get("http://127.0.0.1:8000/namegen")
        deck_name = get_deck_name(browser)
        browser.quit()

        get_spell_cards()
        get_creature_cards()

        print("Creature {0} Spell {1} cards created".format(len(creature_cards), len(spell_cards)))
        print("Spells ", spell_cards)
        print("Creatures ", creature_cards)
        print("MAP", mana_map)
        print("MYM", my_mana_map)

        if len(creature_cards) == creature_count and len(spell_cards) == spell_count and deck_name:
            deck = Deck()
            deck.user_id = user_id
            deck.name = deck_name
            deck.save()

            cards = creature_cards + spell_cards
            deck.card_ids = ":".join([str(c.id) for c in cards])
            deck.save()

            print("Deck \"{0}\" Saved with {1} Creature {2} Spell cards. Total card: {3}".format(
                deck.name, len(creature_cards), len(spell_cards), len(creature_cards) + len(spell_cards)
            ))



def get_spell_cards():
    for i in range(spell_count):
        spell_card = get_random_card(card_type="spell")
        if spell_card:
            my_mana_map[spell_card.mana] += 1
            spell_cards.append(spell_card)

    if len(spell_cards) != spell_count:
        get_spell_cards()

def get_creature_cards():
    for i in range(creature_count):
        creature_card = get_random_card(card_type="creature")
        if creature_card:
            my_mana_map[creature_card.mana] += 1
            creature_cards.append(creature_card)

    if len(creature_cards) != creature_count:
        get_creature_cards()

def get_random_card(card_type):
    cost = randint(1, 7)
    if my_mana_map[cost] < mana_map[cost]:  # still have slot

        card = Card.objects.filter(mana=cost, type=card_type, cardset="set10").order_by("?").first()

        if creature_cards.count(card) < 3 and spell_cards.count(card) < 3:  # allow max 2 same cards in the deck
            return card

    return get_random_card(card_type=card_type)

def get_deck_name(browser):
    browser.execute_script("createJS('holyBooks.js')")
    names = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//ul[@id='myresult']/li"))
    )
    # print("names", names)
    for name in names:
        deck_name = name.text
        if Deck.objects.filter(name=deck_name).count() == 0:
            print("returns {0}".format(deck_name))
            return deck_name

    print("returns nothing")
    # return get_deck_name(browser)
    return None
