from server.spell import Spell
from app.settings import logger


class ReturnHandSpell(Spell):

    def __init__(self, **kwargs):
        self.type = "ReturnHand"

        super(ReturnHandSpell, self).__init__(**kwargs)

    def cast(self, data=None):
        from server.models import Card
        tailored = []
        targets = self.find_target(data)
        for card in targets:

            if not card.player.hand.is_full():
                card.player.ground.remove(card)

                # we have to create new virtual-card to reset changed-properties
                newdbcard = Card.objects.get(pk=card.dbid)
                vcard = newdbcard.to_virtual(card.player)
                vcard.uuid = card.uuid  # we have to use old uuid, client is depending on it when creating new card
                card.player.hand.add(vcard)

                tailored.append({'returned_hand': {
                    'uid': vcard.player.uid,
                    'uuid': vcard.uuid
                }})

        logger.info("spell> ReturnHand cast result:{0}".format(tailored))
        return tailored
