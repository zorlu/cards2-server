from server.spell import Spell
from app.settings import logger

class AddBuffSpell(Spell):
    amount = 0

    def __init__(self, **kwargs):
        self.type = "AddBuff"

        super(AddBuffSpell, self).__init__(**kwargs)

    def cast(self, data=None):
        from . import get_spell_class
        tailored = []
        targets = self.find_target(data)

        for card in targets:
            has_buff = False
            for card_spell in card.spells:
                if card_spell.is_buff:
                    has_buff = True

            # print("Spell> AddBuff cast: has_buff:", has_buff)
            if not has_buff:

                give_dict = self.aura_give.__dict__
                give_dict['card'] = card
                spell_class = get_spell_class(give_dict['type'].lower())
                spell = spell_class(**give_dict)
                for attr_key in give_dict:
                    attr_val = give_dict[attr_key]
                    spell.__setattr__(attr_key, attr_val)

                print("Spell> Addbuff before trigger: ", spell.trigger)
                spell.fix_turn_trigger()
                print("Spell> Addbuff after trigger: ", spell.trigger)



                spell.is_buff = True
                card.spells.append(spell)

                print("Spell> AddBuff cast player: ", card.player.uid, card.spells[0].trigger)

                tailored.append({
                    'buffed': {'uid': card.player.uid, 'uuid': card.uuid, 'desc': give_dict['desc'],
                               'buff_type': "harmful", 'buff_anim': "bomb"}
                })

        logger.info("spell> AddBuff cast result:{0}".format(tailored))
        return tailored
