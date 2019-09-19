from server.card_container import CardContainer

class Graveyard(CardContainer):

    def __init__(self, player):
        self.container_type = "GRAVEYARD"
        super(Graveyard, self).__init__(player)
