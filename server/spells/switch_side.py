from server.spell import Spell
from app.settings import logger

class SwitchSideSpell(Spell):

    def __init__(self, **kwargs):
        self.type = "SwitchSide"

        super(SwitchSideSpell, self).__init__(**kwargs)

    def cast(self, data=None):
        from server.models import Card
        tailored = []
        targets = self.find_target(data)
        for card in targets:

            if not card.alive or card.hp <= 0:  # ex: take control of the destroyer (but destroyer is dead already?)
                continue

            old_uuid = card.uuid
            old_owner = card.player
            new_owner = self.game.get_opposite_player(card.player.uid)

            if not new_owner.ground.is_full():
                slot = new_owner.ground.get_available_slot()
                if slot:
                    old_owner.ground.remove(card)

                    card.uuid = Card.vuuid(new_owner.uid, card.title)
                    card.player = new_owner
                    card.stealed = True  # cannot return hand etc
                    new_owner.ground.add(card, slot=slot)

                    tailored.append({'side_switched': {
                        'from': {
                            'uid': old_owner.uid,
                            'uuid': old_uuid,
                        },
                        'to': {
                            'uid': new_owner.uid,
                            'uuid': card.uuid,
                            'slot': slot
                        }
                    }})

        logger.info("spell> SwitchSide cast result:{0}".format(tailored))
        return tailored
