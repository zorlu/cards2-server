from server.spell import Spell
from app.settings import logger


class DamageSpell(Spell):
    amount = 0

    def __init__(self, **kwargs):
        self.type = "Damage"
        self.amount = kwargs.get('amount')

        super(DamageSpell, self).__init__(**kwargs)

    def cast(self, data=None):
        tailored = []
        targets = self.find_target(data)

        for card in targets:
            card.hp -= self.amount

            tailored.append({
                'dummy': {'uid': card.player.uid, 'uuid': card.uuid, 'textanim': {'text': "-{0}".format(self.amount), 'harmful': True}}
            })

            # if card.is_hp_decreased():
            tailored.append({  # if damaged > make bleeding anyway
                'hp_decreased': {'uid': card.player.uid, 'uuid': card.uuid, 'hp': card.hp}
            })

            if card.hp <= 0:
                tailored.append({
                    'card_died': {'uid': card.player.uid, 'uuid': card.uuid}
                })

                event_result = card.kill(destroyer=self.card)  # trigger game event/auras
                if event_result:
                    tailored += event_result

        logger.info("spell> Damage cast result:{0}".format(tailored))
        return tailored
