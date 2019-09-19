from server.card_container import CardContainer


class Hand(CardContainer):
    def __init__(self, player):
        self.limit = 10
        self.container_type = "HAND"
        super(Hand, self).__init__(player)

    def add(self, vcard):
        vcard.where = "hand"
        super(Hand, self).add(vcard)

    def is_full(self):
        return len(self.cards) == self.limit
