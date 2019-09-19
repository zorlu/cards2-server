from server.card_container import CardContainer
from app.settings import logger


class Ground(CardContainer):
    default_slot = 4
    slots = None
    slot_order = [4, 5, 3, 6, 2, 7, 1, 8, 0, 9]  # ai pick slots in this order when playing creature card

    def __init__(self, player):
        self.slots = [None, None, None, None, None, None, None, None, None, None]
        self.container_type = "GROUND"
        self.limit = 10
        super(Ground, self).__init__(player)

    def get_card_by_uuid(self, uuid):
        for card in self.cards:
            if card.uuid == uuid:
                return card
        return None

    def add(self, card, slot=None):
        card.deployed_turn = self.player.turn.no

        if len(self.cards) == 0:
            slot = self.default_slot
            # logger.info("Ground.add default slot 3 picked for {0}".format(card.title))

        if self.slots[slot]:
            # logger.info("Slot occupied : uid{3} {0} slot{1} {2}".format(card, slot, self.slots, self.player.uid))
            slot = self.get_available_slot()
            if slot == -1:
                raise Exception("No more available slot found!")

            # logger.info("New slot picked {0}".format(slot))

        if slot > -1:
            card.slot_index = slot  # TODO is this reliable?
            self.slots[slot] = card
            super(Ground, self).add(card)

    def remove(self, card):
        slot_index = -1
        for idx, sc in enumerate(self.slots):
            if sc and sc.uuid == card.uuid:
                slot_index = idx
                break

        if slot_index > -1:
            self.slots[slot_index] = None
        # slot_index = self.slots.index(card)
        # if slot_index == 3:
        #    raise Exception("Slot 3 removed! {0}".format(card))
        super(Ground, self).remove(card)

    def is_full(self):
        return len(self.cards) == self.limit

    def get_available_slot(self, excludes=None):
        if self.is_full():
            return -1

        logger.info("Ground> get_available_slots {0}".format(self.slots))
        for slotIndex in self.slot_order:
            if self.slots[slotIndex] is None:
                return slotIndex
        return -1

    def find_slot_by_card(self, card):
        try:
            return self.slots.index(card)
        except IndexError:
            pass
        return -1

    def reset_attacked_this_turn(self):
        for card in self.cards:
            card.attacked_this_turn = False
