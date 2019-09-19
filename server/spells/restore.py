from server.spell import Spell
from app.settings import logger


class RestoreSpell(Spell):
    amount = 0

    def __init__(self, **kwargs):
        self.type = "Restore"
        self.amount = kwargs.get('amount')

        super(RestoreSpell, self).__init__(**kwargs)

    def cast(self, data=None):
        tailored = []
        targets = self.find_target(data)
        for card in targets:

            if card.hp == card.base_hp:
                continue

            elif self.amount == -1:  # -1 amount means full restoration
                card.hp = card.base_hp
            elif card.hp + self.amount > card.base_hp:
                card.hp = card.base_hp

            else:
                card.hp = card.hp + self.amount

            tailored.append({
                'hp_restored': {
                    'uid': card.player.uid,
                    'uuid': card.uuid,
                    'hp': card.hp,
                    'textanim': {
                        'text': "+{0}".format(self.amount),
                        'harmful': False,
                        'onhp': True
                    }
                }
            })

        logger.info("spell> Restore cast result:{0}".format(tailored))
        return tailored
