from server.spell import Spell
from app.settings import logger


class HpSpell(Spell):
    hp = 0

    def __init__(self, **kwargs):
        self.type = "Hp"
        self.hp = kwargs.get('hp')

        super(HpSpell, self).__init__(**kwargs)

    def cast(self, data=None):
        tailored = []
        targets = self.find_target(data)
        for card in targets:
            card.hp += self.hp

            if self.hp >= 0:
                tailored.append({
                    'hp_increased': {
                        'uid': card.player.uid,
                        'uuid': card.uuid,
                        'hp': card.hp,
                        'textanim': {
                            'text': "+{0}".format(self.hp),
                            'harmful': False,
                            'onhp': True
                        }
                    }
                })
            else:
                tailored.append({
                    'hp_decreased': {
                        'uid': card.player.uid,
                        'uuid': card.uuid,
                        'hp': card.hp,
                        'textanim': {
                            'text': "-{0}".format(self.hp),
                            'harmful': True,
                            'onhp': True
                        }
                    }
                })

        logger.info("spell> Hp cast result:{0}".format(tailored))
        return tailored
