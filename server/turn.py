class Turn(object):
    no = 0  # Turn No
    max_cost = 12
    player = None
    cost = 0
    remaining_mana = 0

    def __init__(self, player):
        self.player = player

    def start(self):
        if self.cost + 1 > self.max_cost:
            self.cost = self.max_cost
            self.remaining_mana = self.max_cost
        else:
            self.cost += 1
            self.remaining_mana = self.cost

        self.no += 1

        self.player.ground.reset_attacked_this_turn()  # TODO is it the right place here?

    def to_json(self):
        attackable_cards = []
        for card in self.player.ground.cards:
            # if card.deployed_turn < self.no:
            if card.can_attack():
               attackable_cards.append(card.uuid)

        return {
            'no': self.no,
            'cost': self.cost,
            'whos': self.player.uid,
            'attackables': attackable_cards
        }

    """
    def start(self, players):
        if self.whos_turn is None:
            self.whos_turn = players[random.randint(0, 1)]
        else:
            self.whos_turn = players[0] if self.whos_turn.uid == players[1].uid else players[1]
        self.cost += 1
        self.whos_turn.turn_mana += 1
    """