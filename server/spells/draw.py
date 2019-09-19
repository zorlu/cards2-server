from server.spell import Spell
from server.card import Card
from app.settings import logger


class DrawSpell(Spell):
    amount = 0

    def __init__(self, **kwargs):
        self.type = "Draw"
        self.amount = kwargs.get('amount')

        super(DrawSpell, self).__init__(**kwargs)

    def cast(self, data=None):
        """
        :param data: dict
        :return: list
        """
        target = self.find_target(data)[0]
        if isinstance(target, Card):
            target = target.player

        tailored = [target.draw_card(amount=self.amount, return_tailored=True)]

        logger.info("spell> Draw cast result:{0}".format(tailored))
        return tailored
