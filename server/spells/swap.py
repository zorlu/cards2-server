from server.spell import Spell
from app.settings import logger

class SwapSpell(Spell):

    def __init__(self, **kwargs):
        self.type = "Swap"

        super(SwapSpell, self).__init__(**kwargs)

    def cast(self, data=None):
        tailored = []
        targets = self.find_target(data)
        for card in targets:
            org_hp = card.hp
            org_dp = card.dp

            card.hp = org_dp
            card.dp = org_hp

            tailored.append({'hpdp_swapped': {'uid': card.player.uid, 'uuid': card.uuid, 'hp': card.hp, 'dp': card.dp}})

            if card.hp <= 0 and card.alive:
                tailored.append({'card_died': {'uid': card.player.uid, 'uuid': card.uuid}})
                event_result = card.kill()
                if event_result:
                    tailored += event_result

        logger.info("spell> Swap cast result:{0}".format(tailored))
        return tailored
