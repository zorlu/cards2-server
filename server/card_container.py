import random
from app.settings import logger


class CardContainer(object):
    limit = None
    cards = None
    player = None
    container_type = None
    slots = None

    def __init__(self, player):
        self.cards = []
        self.player = player

    def add(self, vcard):
        if self.limit and len(self.cards) + 1 > self.limit:
            return False

        self.cards.append(vcard)
        if self.container_type != "GRAVEYARD":
            logger.info("{0}.{1}> Add {2} {3}".format(self.container_type, self.player.uid, vcard.title, self.cards))
        return True

    def remove(self, vcard):
        # logger.info("CardContainer> {0} removing {1}".format(self.container_type, vcard))
        if vcard in self.cards:
            self.cards.remove(vcard)
            logger.info("{0}.{1}> Rem {2} {3}".format(self.container_type, self.player.uid, vcard.title, self.cards))
        else:
            print("{0}.{1}> CardNotInHand {2} hand.remove {3}".format(self.container_type, self.player.uid, vcard.title, self.cards))

    def get_card_by_uuid(self, uuid):
        for card in self.cards:
            if card.uuid == uuid:
                return card
        return None

    def get_card_by_dbid(self, dbid):
        for card in self.cards:
            if card.dbid == dbid:
                return card
        return None

    def get_card_by_key(self, key):  # key must be unique for per player
        for card in self.cards:
            if card.key == key:
                return card
        return None

    def get_cards(self, options=None):
        cards = self.cards.copy()

        if not options:
            options = {}

        if "provided" in options:
            cards = options['provided']

        if "exclude" in options:
            if options['exclude'] in cards:
                cards.remove(options['exclude'])

        if "adjacent" in options:
            adjacent_cards = []

            index = options['adjacent'].slot_index
            left_index = index - 1
            right_index = index + 1

            try:
                if self.slots[left_index]:
                    adjacent_cards.append(self.slots[left_index])
            except Exception as err1:
                logger.info("CardContainer> adjacent {0} - left_index: {1}".format(err1, left_index))

            try:
                if self.slots[right_index]:
                    adjacent_cards.append(self.slots[right_index])
            except Exception as err2:
                logger.info("CardContainer> adjacent {0} - right_index".format(err2, right_index))

            cards = adjacent_cards

        if "xtype" in options:  # TODO make card.xtype
            xtype_cards = []
            for card in cards:
                if card.xtype == options['xtype']:
                    xtype_cards.append(card)
            cards = xtype_cards

        if "damaged" in options:  # boolean True=damaged False=undamaged
            damaged_cards = []
            for card in cards:
                if card.is_hp_decreased() == options['damaged']:
                    damaged_cards.append(card)
            cards = damaged_cards

        # TODO make more options (shielded, has aura etc)

        if "defender" in options:
            defender_cards = []
            for card in cards:
                if card.defender and card.defender > 0:
                    defender_cards.append(card)
            cards = defender_cards

        if "canattack" in options:
            canattack_cards = []
            for card in cards:
                if (card.is_creature() and card.dp > 0) == options['canattack']:
                    canattack_cards.append(card)
            cards = canattack_cards

        if "random" in options:
            random.shuffle(cards)

        if "count" in options:  # get n amount of card
            requested = options['count']

            if requested >= len(cards):  # asking count more then we have = give all
                sliced_cards = cards

            else:  # we have enough cards
                sliced_cards = cards[:requested]

            cards = sliced_cards

        if "ignore-immune" not in options:
            # exclude immune cards
            nonimmune_cards = []
            for card in cards:
                if not card.immune:
                    nonimmune_cards.append(card)
            cards = nonimmune_cards

        logger.info("{0}.{1}> get_cards options:{2} cards:{3}".format(self.container_type, self.player.uid, options, [c for c in cards]))

        return cards
