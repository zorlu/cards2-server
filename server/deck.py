from server.card_container import CardContainer
import random


class Deck(CardContainer):

    def __init__(self, player):
        self.container_type = "DECK"
        super(Deck, self).__init__(player)

    def add(self, card):
        self.cards.append(card)
        # random.shuffle(self.cards)

    def shuffle(self, card):
        self.add(card)
        # print("before", [c.key for c in self.cards])
        random.shuffle(self.cards)
        # print("after", [c.key for c in self.cards])

