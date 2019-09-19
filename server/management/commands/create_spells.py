from django.core.management.base import BaseCommand
from server.models import Card, Spell
from random import randint

FRIENDLY_TARGETS = ["player:ground:selected","player:ground:random"]
FRIENDLY_TYPES = ["hp", "dp", "hpdp", "restore"]

ENEMY_TARGETS = ["opponent:ground:selected", "opponent:ground:random"]
ENEMY_TYPES = ["damage", "returnhand", "control", "transform", "swaphpdp", "execute", "shuffle"]
ENEMY_TRANSFORMABLES = [148, 342, 343, 344, 345, 346, 347, 348]

def pick_one(items):
    return items[randint(0, len(items)-1)]


class Command(BaseCommand):
    def handle(self, *args, **options):
        for card in Card.objects.filter(cardset="set10", spell_is_harmful=True):
            if not card.spell_is_harmful:
                for spl in card.spells.all():
                    spl.delete()

                spell = random_friendly_spell()
                card.spells = [spell]
            else:

                for spl in card.spells.all():
                    spl.delete()
                spell = random_harmful_spell()
                card.spells = [spell]




def random_friendly_spell():
    target = pick_one(FRIENDLY_TARGETS)
    stype = pick_one(FRIENDLY_TYPES)

    hp = randint(1, 5)
    dp = hp

    spell = Spell()
    spell.target_key = target
    spell.spell_type = stype
    spell.trigger_key = "play"

    if stype == "hp":
        spell.hp = hp
        spell.desc = "Give +{0} Health".format(hp)

    elif stype == "dp":
        spell.dp = dp
        spell.desc = "Give +{0} Attack".format(dp)

    elif stype == "hpdp":
        spell.hp = hp
        spell.dp = dp
        spell.desc = "Give +{0}/+{1}".format(hp, dp)

    elif stype == "restore":
        spell.amount = hp
        spell.desc = "Restore {0} Health".format(hp)

    if "random" in target:
        spell.desc += " to\\nrandom friendly creature"

    spell.save()
    return spell


def random_harmful_spell():
    target = pick_one(ENEMY_TARGETS)
    stype = pick_one(ENEMY_TYPES)

    spell = Spell()
    spell.target_key = target
    spell.spell_type = stype
    spell.trigger_key = "play"

    if stype == "damage":
        amount = randint(1, 6)
        spell.amount = amount
        spell.desc = "Deal {0} damage".format(amount)

    elif stype == "transform":
        transformable = Card.objects.get(pk=pick_one(ENEMY_TRANSFORMABLES))
        spell.summon = transformable
        spell.desc = "Transform into\\n{0}/{1} {2}".format(transformable.attack, transformable.hp, transformable.title)

    elif stype == "control":
        spell.desc = "Take control"

    elif stype == "returnhand":
        spell.desc = "Return owner's hand"

    elif stype == "swaphpdp":
        spell.desc = "Swap Health and Attack"

    elif stype == "execute":
        spell.desc = "Execute it."

    elif stype == "shuffle":
        spell.desc = "Shuffle into your deck."
        spell.amount = 1

    spell.save()
    return spell