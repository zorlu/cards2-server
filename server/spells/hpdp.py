from server.spell import Spell
from app.settings import logger

class HpDpSpell(Spell):
    hp = 0
    dp = 0

    def __init__(self, **kwargs):
        self.type = "HpDp"
        self.hp = kwargs.get('hp')
        self.dp = kwargs.get('dp')

        super(HpDpSpell, self).__init__(**kwargs)

    def cast(self, data=None):
        tailored = []

        harmful = (self.hp < 0 or self.dp < 0)
        if self.dp > 0:
            text = "+{0}".format(self.dp)
        else:
            text = "{0}".format(self.dp)

        if self.hp > 0:
            text += "/+{0}".format(self.hp)
        else:
            text += "/{0}".format(self.hp)

        # logger.info("HpDp casting data:{0}".format(data['card'].title))
        targets = self.find_target(data)
        for card in targets:
            card.hp += self.hp
            card.dp += self.dp

            textanim = {
                'text': text,
                'harmful': harmful
            }

            command_key = "hp_increased" if  card.is_hp_increased() else "hp_decreased"
            tailored.append({
                command_key: {
                    'uid': card.player.uid,
                    'uuid': card.uuid,
                    'hp': card.hp,
                    'textanim': textanim  # send only once, don't send below
                }
            })

            command_key = "dp_increased" if card.is_dp_increased() else "dp_decreased"
            tailored.append({
                command_key: {
                    'uid': card.player.uid,
                    'uuid': card.uuid,
                    'dp': card.dp,
                    # 'textanim': None  # don't send textanim here, we send it on hp above
                }
            })

        logger.info("spell> HpDp cast result:{0}".format(tailored))
        return tailored
