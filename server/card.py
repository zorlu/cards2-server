from app.settings import simple_logger

class Card(object):
    player = None
    type = "creature"
    family = None
    key = None
    dbid = None
    uuid = None
    title = None
    base_hp = None
    base_dp = None
    hp = None
    dp = None
    mana = None
    revenge = None
    sacrifice = None
    avengeme = False
    defender = None
    together = False
    immune = False
    spells = []
    deployed_turn = None  # when played
    attacked_this_turn = False  # cannot attack more than once
    slot_index = None
    alive = True

    summoned = False
    transformed = False
    stealed = False

    def __init__(self):
        self.base_dp = self.dp
        self.base_hp = self.hp
        self.spells = []

    def __str__(self):
        return self.title

    def __repr__(self):
        return "<Card {0}>".format(self.title)

    @property
    def label(self):
        if self.is_creature():
            return "{0} {1}/{2}".format(self.title, self.dp, self.hp)
        else:
            return self.title

    def to_simple_json(self):
        return {
            'uuid': self.uuid,
            'key': self.key
        }

    def kill(self, destroyer=None):
        if destroyer:
            killer = destroyer.label
        else:
            killer = None

        simple_logger.debug("{0} died, destroyer: {1}".format(self.label, killer))
        self.alive = False
        self.player.ground.remove(self)
        self.player.graveyard.add(self)
        self.player.game.events.unregister(self)

        tailored = []

        if destroyer:
            tailored += self.cast_spell('ondestroy', {'provided': destroyer})

        event_result = self.player.game.events.fire('onauraDestroy', {'triggerer': destroyer, 'card': self})
        if event_result and len(event_result):
            tailored += event_result

        if self.sacrifice and len(self.player.ground.cards):
            for card in self.player.ground.cards:
                card.hp += self.sacrifice
                tailored.append({'hp_increased': {
                    'uid': self.player.uid,
                    'uuid': card.uuid,
                    'hp': card.hp,
                    'textanim': {
                        'text': "Sacrifice +{0}".format(self.sacrifice),
                        'harmful': False
                    }
                }})
        if not len(tailored):
            tailored = []
        return tailored

    def is_hp_decreased(self):  # TODO problematic when enhanged hp decreasing and hp is greater than base_hp
        return self.hp < self.base_hp

    def is_hp_increased(self):
        return self.hp > self.base_hp

    def is_dp_decreased(self):
        return self.dp < self.base_dp

    def is_dp_increased(self):
        return self.dp > self.base_dp

    def can_go_ground(self):
        return self.ami_glowing() and self.is_creature() and not self.player.ground.is_full()

    def ami_glowing(self):
        return self.mana <= self.player.turn.remaining_mana

    def is_creature(self):
        return self.type == "creature"

    def is_spell(self):
        return self.type == "spell"

    def can_attack(self):
        result = self.is_creature() and self.deployed_turn < self.player.turn.no and not self.attacked_this_turn and self.dp > 0
        return result

    def it_dies_i_live(self, target):
        return self.dp >= target.hp and self.hp > target.dp

    def it_dies_i_die(self, target):
        return self.dp >= target.hp and self.hp <= target.dp

    def it_lives_i_die(self, target):
        return self.dp < target.hp and self.hp <= target.dp

    def it_lives_i_live(self, target):
        return self.dp < target.hp and self.hp > target.dp

    def cast_spell(self, key, data=None):
        tailored = []
        for spell in self.spells:
            if spell.trigger == key:
                try:
                    tailored += spell.cast(data)
                except TypeError:
                    print("Card.cast_spell TypeError trigger:", spell.trigger, "target:", spell.target_key, "type:", spell.type, "Card:", self.title)

        return tailored
