from server.spell import Spell
from app.settings import logger

class RemoveBuffSpell(Spell):
    amount = 0

    def __init__(self, **kwargs):
        self.type = "RemoveBuff"
        self.amount = kwargs.get('amount')
        super(RemoveBuffSpell, self).__init__(**kwargs)

    def cast(self, data=None):
        tailored = []
        targets = self.find_target(data)

        for card in targets:
            has_buff = False
            removed_buffs = []
            for card_spell in card.spells:
                if card_spell.is_buff:
                    if len(removed_buffs) < self.amount:
                        removed_buffs.append(card_spell)
            for removed_buff in removed_buffs:
                card.spells.remove(removed_buff)
                tailored.append({
                    'debuffed': {'uid': card.player.uid, 'uuid': card.uuid}
                })

        logger.info("spell> DeBuff cast result:{0}".format(tailored))
        return tailored
