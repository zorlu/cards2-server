from app.settings import logger
import re
from random import randint

class Spell(object):
    game = None
    card = None
    command = None
    type = None  # hpdp/hp/dp/execute/deal-damage
    target_key = None
    targets = None
    trigger = None  # player/opponent:deploy/destroy/draw/attack/turn-begin/end etc
    desc = None
    animation = None
    aura_give = None
    aura_take = None
    aura_condition = None
    is_buff = False
    summon_dbid = None


    def __init__(self, **kwargs):
        self.card = kwargs.get('card')
        self.game = self.card.player.game
        self.desc = kwargs.get('desc')
        self.animation = kwargs.get('animation')
        self.summon_dbid = kwargs.get('summon_dbid')
        self.target_key = kwargs.get('target')
        self.aura_give = kwargs.get('aura_give')
        self.aura_take = kwargs.get('aura_take')

        self.trigger = "on{0}".format(kwargs.get('trigger'))

        self.fix_turn_trigger()  # TODO experimental

        if kwargs.get('aura_condition'):
            self.aura_condition = eval(kwargs.get('aura_condition'))
        # self.game.events.register(self.trigger, self.card)

    def fix_turn_trigger(self):
        old_trigger = self.trigger
        trigger_key = self.trigger
        if "turn:" in trigger_key:

            trigger_parts = trigger_key.split(":")
            # clear triggers when switching spell ownership (like add buff)
            if trigger_parts[-1] == "ai" or re.search("[0-9]+", trigger_parts[-1]):
                del trigger_parts[-1]

                trigger_key = ":".join(trigger_parts)

            if "player" in trigger_key:
                trigger_key = "{0}:{1}".format(trigger_key, self.card.player.uid)
            elif "opponent" in trigger_key:
                trigger_key = "{0}:{1}".format(trigger_key, self.game.get_opposite_player(self.card.player.uid))

            self.trigger = trigger_key

            logger.info("Spell> TurnTriggerFixed: from={0} to={1}".format(old_trigger, trigger_key))


    def find_target(self, data=None):
        """
        who: player/opponent
        where: ground/hand/deck/graveyard
        which: random/selected/all/adjacent/self
        featured: beast/humanoid/damaged/undamaged
        """
        targets = []
        # who, where, which, featured = self.target_key.split(":")

        player = self.card.player
        opponent = self.game.get_opposite_player(player.uid)

        # pick random for ai's choice
        if player.uid == "ai" and ":selected" in self.target_key:
            self.target_key = self.target_key.replace(":selected", ":random")

        if data is None:
            data = {}

        if self.type in ["ReturnHand", "Shuffled"]:  # TODO make it work with container.get_cards
            data['transformed'] = False  # cannot have -> transformed creatures
            data['summoned'] = False # cannot have -> summoned creatures




        provided = data.get('provided')
        if provided and isinstance(provided, str):
            provided_uuid = provided
            uuid_parts = provided_uuid.split("-")
            uid = uuid_parts[0]
            # uuid = "-".join(uuid_parts[1:])
            if uid != "ai":
                uid = int(uid)
            provided_owner = self.game.get_player_by_uid(uid)
            provided = provided_owner.ground.get_card_by_uuid(provided_uuid)
            if not provided:
                provided = provided_owner.hand.get_card_by_uuid(provided_uuid)
                if not provided:
                    provided = provided_owner.deck.get_card_by_uuid(provided_uuid)
                    if not provided:
                        provided = provided_owner.graveyard.get_card_by_uuid(provided_uuid)
                        if not provided:
                            raise Exception("Provided could not be found anywhere uid:{0} uuid:{1}".format(uid,
                                                                                                           provided_uuid))

        # region META SELECTORS
        if self.target_key == "self":
            targets = [self.card]
        elif self.target_key == "provided":
            targets = [provided]
        elif self.target_key == "owner":
            targets = [self.card.player]

        elif self.target_key == "player":
            targets = [player]

        elif self.target_key == "opponent":
            targets = [opponent]

        elif self.target_key == "both":
            targets = [player, opponent]

        elif self.target_key == "opposite":
            if provided.player == player:
                targets = [opponent]
            else:
                targets = [player]

        elif self.target_key == "destroyer":
            targets = [provided]

        elif self.target_key == "attacker":
            targets = [provided]

        elif self.target_key == "adjacent":
            targets = player.ground.get_cards({'adjacent': self.card})

        # elif self.target_key == "summons":
        #    targets = self.summons
            # logger.info("Spell> Target summons: {0}".format(targets))

        elif self.target_key.startswith("unique:"):  # unique creatures like kara-murat
            unique_card_key = self.target_key.split(":")[1]

            targets = []
            unique_card = player.deck.get_card_by_key(key=unique_card_key)
            if not unique_card:
                unique_card = player.hand.get_card_by_key(key=unique_card_key)
                if not unique_card:
                    unique_card = player.ground.get_card_by_key(key=unique_card_key)
                    if not unique_card:
                        unique_card = player.graveyard.get_card_by_key(key=unique_card_key)
            logger.info("Spell> Target {0}: {1}".format(unique_card_key, unique_card))
            if unique_card:
                targets = [unique_card]

        # endregion

        # region BOTH SELECTOR
        elif self.target_key == "both:ground:selected":
            targets = [provided]
        elif self.target_key == "both:ground:random":
            targets = opponent.ground.get_cards({'random': True, 'count': 1, 'exclude': self.card})
            if len(targets) == 0:
                targets = player.ground.get_cards({'random': True, 'count': 1, 'exclude': self.card})
        elif self.target_key == "both:ground:all":
            targets = opponent.ground.get_cards({'exclude': self.card})
            targets += player.ground.get_cards({'exclude': self.card})

        elif self.target_key == "both:ground:random:damaged":
            targets = opponent.ground.get_cards({'exclude': self.card, 'damaged': True})
            targets += player.ground.get_cards({'exclude': self.card, 'damaged': True})

            if len(targets):
                targets = [targets[randint(0, len(targets)-1)]]

        # endregion

        # region PLAYER SELECTOR
        elif self.target_key == "player:ground:selected":
            targets = [provided]
        elif self.target_key == "player:ground:all":
            targets = player.ground.get_cards({'exclude': self.card})

        elif self.target_key == "player:ground:random":
            targets = player.ground.get_cards({'random': True, 'count': 1, 'exclude': self.card})

        elif self.target_key == "player:ground:random:damaged":
            targets = player.ground.get_cards({'random': True, 'damaged': True, 'count': 1, 'exclude': self.card})
        # endregion

        # region OPPONENT SELECTOR
        elif self.target_key == "opponent:ground:selected":
            targets = [provided]
        elif self.target_key == "opponent.ground:all":
            targets = opponent.ground.get_cards({'exclude': self.card})

        elif self.target_key == "opponent:ground:random":
            targets = opponent.ground.get_cards({'random': True, 'count': 1, 'exclude': self.card})

        elif self.target_key == "opponent:ground:random:damaged":
            targets = opponent.ground.get_cards({'random': True, 'damaged': True, 'count': 1, 'exclude': self.card})
        # endregion


        """
        if player.uid == "ai" and which == "selected":
            which = "random"

        target_cards = []
        card_containers = []
        target_player = opponent  # by default

        if who == "player":
            target_player = player
        elif who == "oppoent":
            target_player = opponent
        elif who == "both":
            target_player = [player, opponent]


        if where == "hand":
            if who == "both":
                card_containers = [player.hand, opponent.hand]
            else:
                card_containers = [target_player.hand]

        elif where == "ground":
            if who == "both":
                card_containers = [player.ground, opponent.ground]
            else:
                card_containers = [target_player.ground]
        elif where == "deck":
            if who == "both":
                card_containers = [player.deck, opponent.deck]
            else:
                card_containers = [target_player.deck]
        # TODO battleground


        if featured == "damaged":
            options['damaged'] = True


        if which == "self":
            target_cards = [self.card]
        elif which == "owner":
            target_cards = [self.card.player]

        elif which == "random":
            options.update({'random': True, 'count': 1, 'exclude': self.card})
            for card_container in card_containers:
                target_cards += card_container.get_cards(options)

        elif which == "all":
            for card_container in card_containers:
                target_cards += card_container.get_cards(options)

        elif which == "adjacent":
            adjacents = card_containers[0].get_cards({'adjacent': self.card})  # adjacent does not have who=both

            if adjacents[0] is not None:
                target_cards.append(adjacents[0])
            if adjacents[1] is not None:
                target_cards.append(adjacents[1])

        elif which == "selected":
            card_container = card_containers[0]
            logger.info("card_container> TYPE:{0}".format(card_container.container_type))

            if isinstance(data['provided'], str):
                target_card = card_container.get_card_by_uuid(data['provided'])
            else:
                target_card = data['provided']
            target_cards = card_container.get_cards({'provided': [target_card]})
        # TODO make more target type (xtype, damaged etc)
        """
        logger.info("Spell> {2} find_target {0} trigger:{3} result:{1}".format(self.target_key, targets, self.type, self.trigger))
        return targets
