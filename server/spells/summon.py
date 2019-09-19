from server.spell import Spell
from app.settings import logger, simple_logger


class SummonSpell(Spell):
    amount = 1

    def __init__(self, **kwargs):
        self.type = "Summoned"
        self.amount = kwargs.get('amount', 1)

        super(SummonSpell, self).__init__(**kwargs)

    def cast(self, data=None):
        from server.models import Card
        tailored = []
        targets = self.find_target(data)

        for player in targets:
            for i in range(self.amount):

                newdbcard = Card.objects.get(pk=self.summon_dbid)
                vcard = newdbcard.to_virtual(player)

                slot = player.ground.get_available_slot()
                if slot > -1:
                    vcard.summoned = True  # cannot return to hand etc.
                    player.ground.add(vcard, slot)
                    tailored.append({
                        'summoned': {
                            'uid': player.uid,
                            'uuid': vcard.uuid,
                            'key': vcard.key,
                            'slot': slot
                        }
                    })
                    simple_logger.debug("{0} summoned {1}".format(player.name, vcard.label))

        logger.info("spell> SummonSpell cast result:{0}".format(tailored))
        return tailored
