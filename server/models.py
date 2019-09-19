from django.db import models
from django.contrib.auth.models import User
from server.card import Card as VirtualCard
from server.player import Player as VirtualPlayer
from server.spells import *
from slugify import slugify
from time import time
import random


SPELL_TYPES = (
    ('aura', "AURA"),
    ('hp', "HP"),
    ('dp', "DP"),
    ('hpdp', "HPDP"),
    ('damage', "Damage"),
    ('swaphpdp', "Swap Hp <-> Dp"),
    ('restore', "Restore"),
    ('mana', "Mana"),
    ('token', "Token (Target: Champion)"),
    ('draw', "Draw"),
    ('discard', "Discard (Hand)"),
    ('shield', "Shield"),
    ('tank', "Tank (Taunt)"),
    ('greatshield', "Great Shield"),
    ('dattack', "Double Attack"),
    ('locknloaded', "Lock & Loaded"),
    ('returnhand', "Return to Hand"),
    ('control', "Control / Steal"),
    ('summon', "Summon"),
    ('freeze', "Freeze"),
    ('attack', "Auto-Attack"),
    ('transform', "Transform"),
    ('addbuff', "Add Buff"),
    ('removebuff', "Remove Buff"),

    ('shuffle', "Shuffle In Deck"),
    ('execute', "Execute"),
    ('dummy', "Dummy"),
)
SPELL_TARGET_KEYS = (
    ('self', "Self"),
    ('owner', "Card Owner (This Card)"),
    ('player', "Player"),
    ('opponent', "Opponent"),
    ('both', "Player & Opponent"),
    ('opposite', "Opposite Player <-> Opponent"),

    ('destroyer', "Destroyer (Trigger: destroy)"),
    ('attacker', "Attacker (Trigger: attack)"),
    ('adjacent', "Adjacent"),
    ('summons', "Summons (in 'creatures' field)"),
    ('unique:karamurat', "unique:karamurat - (My Kara Murat)"),
    ('aura:owner', "aura:owner"),
    ('aura:target', "aura:target"),
    ('aura:ground:infected:', "aura:ground:infected"),

    # both sides
    ('', ''),
    ('', "########### BOTH SIDE ###########"),
    ('both:ground:all', "both:ground:all"),
    ('both:ground:random:', "both:ground:random"),
    ('both:ground:all:damaged', "both:ground:all:damaged"),
    ('both:ground:random:damaged', "both:ground:random:damaged"),
    ('both:ground:all:undamaged', "both:ground:all:undamaged"),
    ('both:ground:random:undamaged', "both:ground:random:undamaged"),

    ('both:ground:selected', "both:ground:selected"),
    ('both:ground:selected:creature', "both:ground:selected:creature"),
    ('both:ground:selected:damaged', "both:ground:selected:damaged"),
    ('both:ground:selected:undamaged', "both:ground:selected:undamaged"),

    # player's side
    ('', ''),
    ('', "########### PLAYER ###########"),
    ('player:hand:random', "player:hand:random"),
    ('player:hand:all', "player:hand:all"),
    ('player:deck:random', "player:deck:random"),
    ('player:deck:all', "player:deck:all"),

    ('player:ground:random', "player:ground:random"),
    ('player:ground:all', "player:ground:all"),
    ('player:ground:random:damaged', "player:ground:random:damaged"),
    ('player:ground:all:damaged', "player:ground:all:damaged"),
    ('player:ground:random:undamaged', "player:ground:random:undamaged"),
    ('player:ground:all:undamaged', "player:ground:all:undamaged"),
    ('player:ground:selected', "player:ground:selected"),
    ('player:ground:selected:creature', "player:ground:selected:creature"),
    ('player:ground:selected:damaged', "player:ground:selected:damaged"),
    ('player:ground:selected:undamaged', "player:ground:selected:undamaged"),
    # TODO creature subtype specific targes (pground:mechanic:random, oground:beast:provided)

    # opponent's side
    ('', ''),
    ('', "########### OPPONENT ###########"),
    ('opponent:hand:random', "opponent:hand:random"),
    ('opponent:hand:all', "opponent:hand:all"),
    ('opponent:deck:random', "opponent:deck:random"),
    ('opponent:deck:all', "opponent:deck:all"),

    ('opponent:ground:random', "opponent:ground:random"),
    ('opponent:ground:all', "opponent:ground:all"),
    ('opponent:ground:random:damaged', "opponent:ground:random:damaged"),
    ('opponent:ground:all:damaged', "opponent:ground:all:damaged"),
    ('opponent:ground:random:undamaged', "opponent:ground:random:undamaged"),
    ('opponent:ground:all:undamaged', "opponent:ground:all:undamaged"),
    ('opponent:ground:selected', "opponent:ground:selected"),
    ('opponent:ground:selected:creature', "opponent:ground:selected:creature"),
    ('opponent:ground:selected:damaged', "opponent:ground:selected:damaged"),
    ('opponent:ground:selected:undamaged', "opponent:ground:selected:undamaged"),
)

SPELL_TRIGGER_KEYS = (
    ('play', 'Play Spell Card'),
    ('deploy', 'Deploy'),
    ('draw', 'Draw (This Card)'),
    ('discard', 'Discard (This Card)'),
    ('destroy', 'Destroy'),
    ('amp', 'Anger Management'),
    ('htp', 'Healing Touch'),
    ('defense', 'Defense - This Card'),
    ('attack', 'Attack - This Card'),
    ('restore', 'Whenever Heal'),
    ('player:turn:begin', "Beginning of Player's Turn"),
    ('player:turn:end', "End of Player's Turn"),
    ('turn:begin', "Beginning of a Turn"),
    ('turn:end', "End of a Turn"),

    ('', "---- AURA ----"),
    ('auraPlay', "onAuraPlay"),
    ('auraDestroy', "onAuraDestroy"),
    ('auraHeal', "onAuraHeal"),
    ('auraDefense', "onAuraDefense"),
    ('auraAttack', "onAuraAttack"),
    ('auraDraw', "onAuraDraw"),
    ('auraDiscard', "onAuraDiscard"),
    ('auraSummon', "onAuraSummon"),
)


class Spell(models.Model):
    spell_type = models.CharField(max_length=100, choices=SPELL_TYPES)  # hpdp / damage / hp / dp etc
    target_key = models.CharField(max_length=100, choices=SPELL_TARGET_KEYS)  # player:ground:random etc
    trigger_key = models.CharField(max_length=100, choices=SPELL_TRIGGER_KEYS)  # when trigger?
    animation = models.CharField(max_length=20, null=True, blank=True)
    # target_count = models.IntegerField() TODO player:ground:random:2
    desc = models.CharField(max_length=200, null=True, blank=True)
    hp = models.SmallIntegerField(null=True, blank=True) # 1 = +1, 2 = +2, -1 = -1, -2 = -2
    dp = models.SmallIntegerField(null=True, blank=True)
    amount = models.SmallIntegerField(null=True, blank=True)  # damage 1 etc
    aura_give = models.ForeignKey("server.Spell", null=True, blank=True, related_name="aura_gives")
    aura_take = models.ForeignKey("server.Spell", null=True, blank=True, related_name="aura_takes")
    summon = models.ForeignKey("server.Card", null=True, blank=True)
    # aura_give_id = models.IntegerField(null=True, blank=True) # trigger spell when give aura
    # aura_take_id = models.IntegerField(null=True, blank=True) # trigger spell when take back aura
    aura_condition = models.TextField(null=True, blank=True)
    """ aura_condition = models.TextField()
    onCardDestroy: Whenever a friendly robot dies, draw a card?
        {
         "when": {"owner": "player", "xtype": "robot"}
        }
        onCardPlay: whenever you play a 1-attack minion, give it +2/+2?
        "when": {"owner": "player", "cardType": "creature", "dp": "1"},

        onCardHeal: whenever a character healed, deal 1 damage to a random enemy?
        "when": {}
    }
    """
    def __str__(self):
        return "<{1}:{0} {2}/{3}>".format(self.id, self.spell_type, self.target_key, self.trigger_key)

    def to_virtual(self, owner_card):
        vspell = None
        spell_class = get_spell_class(self.spell_type)  # in spells.__init__
        if spell_class:
            aura_take = None
            aura_give = None
            summon_id = None

            if self.aura_give:
                aura_give = self.aura_give.to_virtual(owner_card)
            if self.aura_take:
                aura_take = self.aura_take.to_virtual(owner_card)
            if self.summon:
                summon_id = self.summon.id

            vspell = spell_class(card=owner_card, hp=self.hp, dp=self.dp, amount=self.amount,
                                 target=self.target_key, trigger=self.trigger_key, desc=self.desc,
                                 aura_give=aura_give, aura_take=aura_take,
                                 aura_condition=self.aura_condition, animation=self.animation, summon_dbid=summon_id)
        return vspell


PLAYER_CLASSES = (
    ('system', 'system'),
    ('priest', 'priest'),
    ('warlock', 'warlock'),
    ('paladin', 'paladin'),
    ('warrior', 'warrior'),
    ('rogue', 'rogue'),
    ('druid', 'druid'),
    ('shaman', 'shaman'),
    ('mage', 'mage'),
    ('hunter', 'hunter')
)
CARD_SETS = (
    ('set01', 'Basic'),
    ('set02', 'set02'),
    ('set03', 'set03'),
    ('set04', 'set04'),
    ('set05', 'set05'),
    ('set06', 'set06'),
    ('set07', 'set07'),
    ('set08', 'set08'),
    ('set09', 'set09'),
    ('set10', 'The Glory Era'),
    ('set11', 'set11'),
    ('set12', 'set12'),
    ('set13', 'set13'),
    ('set14', 'set14'),
    ('set15', 'set15'),
    ('set16', 'set16'),
    ('set17', 'set17'),
    ('set18', 'set18'),
    ('set19', 'set19'),
    ('set20', 'set20')
)
CREATURE_FAMILIES = (
    ('beast', "Beast"),
    ('demon', "Demon"),
    ('undead', "Undead"),
    ('elemental', "Elemental")
)


class Card(models.Model):
    key = models.CharField(max_length=250, null=True, blank=True)
    # pclass = models.CharField(max_length=10, choices=PLAYER_CLASSES)
    type = models.CharField(max_length=10, choices=(('creature', "creature"), ('spell', 'spell'), ('player', 'player')))
    # features = models.CharField(max_length=10, null=True, blank=True, help_text="R(evenge) T(ank)")  # R = revenge
    family = models.CharField(max_length=20, null=True, blank=True, choices=CREATURE_FAMILIES)
    # collectible = models.BooleanField(default=False)
    cardset = models.CharField(max_length=10, choices=CARD_SETS, default="set01")
    revenge = models.PositiveSmallIntegerField(null=True, blank=True)  # gain +n dp before counter-attack
    sacrifice = models.PositiveSmallIntegerField(null=True, blank=True)  # give +n hp to all allies
    avengeme = models.BooleanField(default=False)  # when i die, random ally attack to destoryer
    defender = models.BooleanField(default=False)  # attack me instead
    together = models.BooleanField(default=False)  # attach together
    immune = models.BooleanField(default=False)  # cannot be spell target

    title = models.CharField(max_length=100)
    portrait = models.CharField(max_length=100, null=True, blank=True) # https://photos.google.com/share/AF1QipNy13qQiGcGQm9QHVqcliduskYfwG9mlEFoL10u8im0GMrdojkTdS33VOfqThZLMg?key=aXcxbUw1TDVaMjhTSE5BRjlOdm5MeFdxUE1KY0FB
    hp = models.SmallIntegerField(default=0)
    attack = models.SmallIntegerField(default=0)
    mana = models.SmallIntegerField(default=0)
    spells = models.ManyToManyField(Spell, blank=True)
    copy_protected = models.BooleanField(default=False)  # could not be copied/shuffled/steal etc.
    spell_is_harmful = models.BooleanField(default=False)

    def save(self, **kwargs):
        is_new = self.pk is None
        super(Card, self).save(**kwargs)
        if is_new:
            self.key = "{0}_{1}".format(self.type, slugify(self.title))
            super(Card, self).save()

    def __str__(self):
        return self.title

    @property
    def label(self):
        if self.type == "creature":
            return "{0} {1}/{2}".format(self.title, self.attack, self.hp)
        else:
            return self.title

    def spells_for_admin(self):
        return ", ".join(map(str, self.spells.all()))
    spells_for_admin.short_description = "Spells"

    def description_for_admin(self):
        return self.get_description()
    description_for_admin.short_description = "Desc"

    @staticmethod
    def vuuid(user_id, card_title):
        return "{0}-{1}-{2}".format(user_id, slugify(card_title), time())

    def get_description(self):
        descs = []
        if self.revenge:
            descs.append("FEAT:Revenge +{0}".format(self.revenge))
        elif self.sacrifice:
            descs.append("FEAT:Sacrifice +{0}".format(self.sacrifice))
        elif self.defender:
            descs.append("FEAT:Defender")
        elif self.avengeme:
            descs.append("FEAT:Avenge Me!")
        elif self.together:
            descs.append("FEAT:Together")

        if self.immune:
            descs.append("FEAT:Immune")

        for spell in self.spells.all():
            descs.append(spell.desc)

        result = "\\n".join(descs)
        return result

        # return "Give +1/+1 to all friendly creatures."

    def to_json(self, user_id=None):
        result = {
            'dbid': self.id,
            'key': self.key,
            'type': self.type,
            'family': "-{0}-".format(self.get_family_display()) if self.family else "",
            'title': self.title,
            'desc': self.get_description(),
            # 'revenge': self.revenge,
            # 'sacrifice': self.sacrifice,
            # 'avengeme': self.avengeme,
            # 'defender': self.defender,
            # 'together': self.together,
            'img': self.portrait,
            'hp': self.hp,
            'attack': self.attack,
            'mana': self.mana,
            'selector': None,
            'auraowner': False,
            'copyprotected': self.copy_protected
        }
        if user_id:
            result['uuid'] = Card.vuuid(user_id, self.title)
            result['uid'] = user_id

        deploy_spell = self.spells.filter(trigger_key__in=["deploy", "play"], target_key__contains=":selected").first()
        if deploy_spell:
            result['selector'] = deploy_spell.target_key  # tell client this card needs to activate targetSelector before deploying
        if self.spells.filter(spell_type='aura').first():
            result['auraowner'] = True
        return result

    def to_virtual(self, player):
        vcard = VirtualCard()
        vcard.player = player
        vcard.dbid = self.id
        vcard.uuid = self.vuuid(player.uid, self.title)
        vcard.title = self.title
        vcard.desc = self.get_description()
        vcard.revenge = self.revenge
        vcard.sacrifice = self.sacrifice
        vcard.avengeme = self.avengeme
        vcard.defender = self.defender
        vcard.together = self.together
        vcard.immune = self.immune  # cannot be targeted by spells
        vcard.img = self.portrait
        vcard.key = self.key
        vcard.hp = self.hp
        vcard.base_hp = self.hp
        vcard.dp = self.attack
        vcard.base_dp = self.attack
        vcard.mana = self.mana
        vcard.type = self.type
        vcard.family = self.family
        vcard.copyprotected = self.copy_protected

        # TODO - simple spells
        for db_spell in self.spells.all().order_by('-spell_type'):
            vcard.spells.append(db_spell.to_virtual(vcard))

        return vcard


class Player(models.Model):
    user = models.OneToOneField(User, related_name="player")
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    @property
    def first_deck(self):
        return self.user.decks.all().first()  # TODO must be user-requested

    def to_virtual(self, game):
        player = VirtualPlayer(game=game)
        player.uid = self.id
        player.name = self.name
        return player


class Deck(models.Model):
    cards = []
    user = models.ForeignKey(User, related_name="decks")
    name = models.CharField(max_length=30, default="Beginner")
    card_ids = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return "{0} ({1} cards)".format(self.name, self.card_count)

    @property
    def card_count(self):
        return len(self.card_ids.split(":"))

    def get_cards(self, randomize=False):
        if len(self.cards) == 0:
            cards = []
            card_ids = list(map(int, self.card_ids.split(":")))
            for cid in card_ids:
                cards.append(Card.objects.get(pk=cid))

            if randomize:
                random.shuffle(cards)
            self.cards = cards
        return self.cards

    def cards_for_admin(self):
        result = {}
        for card in self.get_cards():
            if card.key not in result:
                result[card.key] = {'count': 0, 'label': None, 'mana': None}

            result[card.key]['count'] += 1
            result[card.key]['label'] = card.label
            result[card.key]['mana'] = card.mana

        html = ""
        for k in result:
            item = result[k]
            html += "({0}){1} {2}<br/>".format(item['count'], item['label'], item['mana'])

        return html
    cards_for_admin.short_description = "Cards"
    cards_for_admin.allow_tags = True


class Dungeon(models.Model):
    name = models.CharField(max_length=100)
    total_stages = models.IntegerField(default=1)
    cardback_image = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class DungeonStage(models.Model):
    dungeon = models.ForeignKey(Dungeon, related_name="stages")
    no = models.IntegerField(default=1)
    boss_name = models.CharField(max_length=50)
    boss_hp = models.IntegerField(default=30)
    boss_portrait = models.CharField(max_length=50)
    boss_deck = models.ForeignKey(Deck, null=True, on_delete=models.SET_NULL)
    next_stage = models.ForeignKey("server.DungeonStage", null=True, blank=True, related_name="next_stages")

    def __str__(self):
        return "{0} Stage {1}".format(self.dungeon, self.no)
