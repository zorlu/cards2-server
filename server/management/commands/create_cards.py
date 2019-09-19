from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from server.models import Card
from random import randint

from app.fractal import Fractal
from app import settings
import os


class Command(BaseCommand):
    def handle(self, *args, **options):

        browser = webdriver.PhantomJS()
        browser.implicitly_wait(30)

        browser.get("http://127.0.0.1:8000/namegen")

        # gen_spell_cards(browser, number_of_cards=10)
        gen_creature_cards(browser, number_of_cards=10)

        browser.quit()

def gen_creature_cards(browser, number_of_cards=1):
    browser.execute_script("createJS('classNames.js')")
    WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//span[@id='options']/input")))

    for i in range(number_of_cards):
        browser.execute_script("mynameGen(1)")
        names = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//ul[@id='myresult']/li"))
        )
        for name in names:
            card_title = name.text
            if Card.objects.filter(title=card_title).first() is None:
                card = Card()
                card.type = "creature"
                card.cardset = "set10"
                card.title = card_title
                card.hp = randint(1, 8)
                card.attack = randint(1, 6)
                card.mana = randint(1, 7)
                card.save()
                card.portrait = generate_portrait("{0}.png".format(card.key))
                card.save()
                print("CreatureCard created: {0}".format(card.title))

def gen_spell_cards(browser, number_of_cards=1):
    for i in range(number_of_cards):
        browser.execute_script("createJS('spellNames.js')")
        names = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//ul[@id='myresult']/li"))
        )
        print("Collecting Names: {0} {1}".format(i, len(names)))
        for name in names:
            card_title = name.text
            if Card.objects.filter(title=card_title).first() is None:
                card = Card()
                card.type = "spell"
                card.cardset = "set10"
                card.title = card_title
                card.hp = 0
                card.dp = 0
                card.mana = randint(1, 6)
                card.save()

                card.portrait = generate_portrait("{0}.png".format(card.key))
                card.save()
                print("SpellCard created: {0}".format(card.title))


def generate_portrait(filename):
    output_dir = os.path.join(settings.BASE_DIR, "client", "img", "portraits")
    f = Fractal(490, 420, 1)
    return f.generate(filename, output_dir)
