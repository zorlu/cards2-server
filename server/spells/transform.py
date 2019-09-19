from server.spell import Spell
from app.settings import logger

class TransformSpell(Spell):

    def __init__(self, **kwargs):
        self.type = "Transformed"


        super(TransformSpell, self).__init__(**kwargs)

    def cast(self, data=None):
        from server.models import Card
        tailored = []
        targets = self.find_target(data)

        logger.info("Transform> summons: {0}".format(self.summon_dbid))

        for card in targets:
            player = card.player

            slot = player.ground.find_slot_by_card(card)
            if slot > -1:
                to_card_id = self.summon_dbid

                to_card = Card.objects.get(pk=to_card_id).to_virtual(player)
                # to_card = self.card.summons.first().to_virtual(card.player)  # self.card.summons = manytomany field
                to_card.transformed = True  # cannot return hand or shuffle in deck
                player.ground.remove(card)
                player.ground.add(to_card, slot)

                tailored.append({
                    'transformed': {
                        'from': {
                            'uid': player.uid,
                            'uuid': card.uuid,
                            'slot': slot
                        },
                        'to': {
                            'uid': player.uid,
                            'uuid': to_card.uuid,
                            'key': to_card.key,
                            'slot': slot
                        }
                    }
                })


        logger.info("spell> TransformSpell cast result:{0}".format(tailored))
        return tailored
