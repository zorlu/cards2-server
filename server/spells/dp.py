from server.spell import Spell
from app.settings import logger

class DpSpell(Spell):
    dp = 0

    def __init__(self, **kwargs):
        self.type = "Dp"
        self.dp = kwargs.get('dp')

        super(DpSpell, self).__init__(**kwargs)

    def cast(self, data=None):
        tailored = []

        targets = self.find_target(data)
        for card in targets:
            card.dp += self.dp

            if self.dp >= 0:
                tailored.append({
                    'dp_increased': {
                        'uid': card.player.uid,
                        'uuid': card.uuid,
                        'dp': card.dp,
                        'textanim': {
                            'text': "+{0}".format(self.dp),
                            'harmful': False,
                            'ondp': True
                        }
                    }
                })
            else:
                tailored.append({
                    'dp_decreased': {
                        'uid': card.player.uid,
                        'uuid': card.uuid,
                        'dp': card.dp,
                        'textanim': {
                            'text': "-{0}".format(self.dp),
                            'harmful': True,
                            'ondp': True
                        }
                    }
                })

        logger.info("spell> Dp cast result:{0}".format(tailored))
        return tailored
