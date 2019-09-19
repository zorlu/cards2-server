from server.spell import Spell
from server.player import Player
from app.settings import logger


class ShuffleSpell(Spell):
    amount = 1

    def __init__(self, **kwargs):
        self.type = "Shuffled"
        self.amount = kwargs.get('amount', 1)

        super(ShuffleSpell, self).__init__(**kwargs)

    def cast(self, data=None):
        from server.models import Card
        tailored = []
        targets = self.find_target(data)

        for card in targets:

            if self.summon_dbid:  # in this case, spell target must be pointing to the Player
                card_dbid = self.summon_dbid
            else:  # if shuffling card not specified in the summon field, target must be pointing to a Card
                card_dbid = card.dbid

            for i in range(self.amount):
                newdbcard = Card.objects.get(pk=card_dbid)
                vcard = newdbcard.to_virtual(self.card.player)
                self.card.player.deck.shuffle(vcard)  # TODO check this, looks not shuffling array

                shuffle_data = {
                    'shuffled': {
                        'deck_count': len(vcard.player.deck.cards),
                        'copy': {
                            'uid': vcard.player.uid,
                            'uuid': vcard.uuid,
                            'key': vcard.key
                        }
                    }
                }
                # if target is a Card(x:ground:x or summon_db_id), not a Player(spell_target=cardowner)
                if not isinstance(card, Player):
                    shuffle_data['original'] = {
                        'uid': card.player.uid,
                        'uuid': card.uuid,
                        'key': card.key
                    }
                tailored.append(shuffle_data)

        logger.info("spell> ShuffleSpell cast result:{0}".format(tailored))
        return tailored
