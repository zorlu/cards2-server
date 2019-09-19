from server.card import Card
from server.spell import Spell
from app.settings import logger

class AuraSpell(Spell):

    def __init__(self, **kwargs):
        self.type = "Aura"
        super(AuraSpell, self).__init__(**kwargs)

    def cast(self, data=None):
        logger.info("Events> Aura registering {0} {1}".format(self.aura_give.trigger, self.card.title))
        self.game.events.register(
            key=self.aura_give.trigger,
            card=self.card,
            callback=self.give_handler,
            unregister_callback=self.take_handler
        )
        return []

    def give_handler(self, event_data=None):
        from server.spells import get_spell_class

        # print("give_handler aura_condition: ", self.aura_give.aura_condition)

        if self.aura_give.aura_condition and not self.check_condition(self.aura_give.aura_condition, event_data):
            return False

        player = self.card.player  # aura-owner card's owner is a player1
        opponent = self.card.player.game.get_opposite_player(player.uid)  # player2
        cast_data = {}

        give_dict = self.aura_give.__dict__
        # print("give_dict: ", "data", give_dict)

        spell_class = get_spell_class(give_dict['type'].lower())
        spell = spell_class(card=event_data['card'])

        for attr_key in give_dict:
            attr_val = give_dict[attr_key]
            spell.__setattr__(attr_key, attr_val)

        if spell.target_key == "aura:owner":
            target = self.card
        elif spell.target_key == "aura:target":

            if event_data['card'] == self.card:  # aura:owner cannot be aura:target
                return False

            target = event_data['card']
        elif spell.target_key == "player":
            target = player
        elif spell.target_key == "opponent":
            target = opponent
        elif "target" in event_data and event_data['target']:
            target = event_data['target']
        else:
            target = spell.find_target(event_data)
            if len(target):  # always returns array
                target = target[0]
            else:
                # raise Exception("Unknown aura-give-target target:{0} data:{1} spell:{2}".format(spell.target_key, event_data, spell.__dict__))
                logger.info("Aura> No available target found for key:{0} data:{1}".format(spell.target_key, event_data))
                return False

        if isinstance(target, Card) and not target.alive:
            logger.info("Aura> Target is dead already! key:{0} target:{1}".format(spell.target_key, target.title))
            return False

        # print("target is?? ", spell.target_key, target)

        cast_data['provided'] = target
        spell.target_key = "provided"  # override
        tailored = spell.cast(cast_data)

        if not tailored:
            tailored = []

        tailored.append({
            'aura_triggered': {'uid': player.uid, 'uuid': self.card.uuid}
        })
        return tailored


    def take_handler(self):
        return None

    def check_condition(self, aura_condition, event_data):
        player = self.card.player  # aura-owner card's owner is a player1
        opponent = self.card.player.game.get_opposite_player(player.uid)  # player2

        compiled_condition = {}
        for k in aura_condition:

            v = aura_condition[k]

            if v == "aura:owner":
                compiled_condition[k] = self.card
            elif v == "player":
                compiled_condition[k] = player
            elif v == "opponent":
                compiled_condition[k] = opponent
            else:
                compiled_condition[k] = v

            if "." in k:  # {'card.type': "creature", 'card.hp': 1} == 1hp creaure card
                parts = k.split(".")
                event_data[k] = event_data[parts[0]].__getattribute__(parts[1])

        for k in compiled_condition:
            if k not in event_data:
                raise Exception("AuraSpell.check_condition Condition key is missing {0}".format(k))

            if event_data[k] != compiled_condition[k]:
                logger.info("Events> Condition not equal {0} > {1} != {2}".format(k, event_data[k], compiled_condition[k]))
                return False
            else:
                logger.info("Events> Condition equal! {0} > {1} == {2}".format(k, event_data[k], compiled_condition[k]))

        logger.info("Events> All conditions are equal!!!")
        return True

    """
    def give_handler(self, data=None):
        player = self.card.player  # aura-owner card's owner is a player1
        opponent = self.card.player.game.get_opposite_player(player.uid)  # player2

        give_spell = self.aura_give.to_virtual(self.card)
        logger.info("Events> Aura give-handler trigger={0}, uid={4} card={1} data={2} condition={3}".format(
            give_spell.trigger, self.card.title, data, give_spell.aura_condition, player.uid))

        if data is None:
            data = {}

        target = None
        if give_spell.target_key == "aura:owner":
            target = self.card
        elif give_spell.target_key == "owner":
            target = player

        give_spell.target_key = "provided"

        # check aura conditions
        conditions = give_spell.aura_condition
        is_all_conditions_true = True  # pass if no condition
        if conditions:
            total_conditions = len(conditions.keys())
            true_conditions = 0

            if conditions.get("owner") == "player"and data['triggerer'].player == player:
                true_conditions += 1
            elif conditions.get("owner") == "opponent" and data['triggerer'].player == opponent:
                true_conditions += 1

            if conditions.get("destroyer-owner") == "player" and data['triggerer'].player == player:
                true_conditions += 1
            elif conditions.get("destroyer-owner") == "opponent" and data['triggerer'].player == opponent:
                    true_conditions += 1

            if conditions.get("victim") == "aura:owner" and data['victim'] == self.card:
                    true_conditions += 1
            elif conditions.get("attacker") == "aura:owner" and data['attacker'] == self.card:  # TODO check spell target
                true_conditions += 1

            if true_conditions != total_conditions:
                is_all_conditions_true = False

        if is_all_conditions_true:
            tailored = give_spell.cast({'provided': target})
            if not tailored:
                tailored = []
            tailored.append({
                'aura_triggered': {'uid': self.card.player.uid, 'uuid': self.card.uuid}
            })
            return tailored
        else:
            logger.info("Events> Aura condition false {0}".format(give_spell.aura_condition))
            return []
    """