from server.spell import Spell
from app.settings import logger


class ExecuteSpell(Spell):

    def __init__(self, **kwargs):
        self.type = "Execute"

        super(ExecuteSpell, self).__init__(**kwargs)

    def cast(self, data=None):
        tailored = []
        targets = self.find_target(data)

        for card in targets:

            if card.alive:
                tailored.append({
                    'card_died': {
                        'uid': card.player.uid, 'uuid': card.uuid, 'attach': 'execute', 'textanim': {'text': "Executed", 'harmful': True}
                    }})

                event_result = card.kill(destroyer=self.card)  # trigger game event/auras
                if event_result:
                    tailored += event_result

        logger.info("spell> Execute cast result:{0}".format(tailored))
        return tailored
