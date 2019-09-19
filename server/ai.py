from random import randint
import itertools

from server.command import Command
import time
from app.settings import logger


class AI(object):
    player = None

    def __init__(self, player):
        self.player = player

    def play_your_turn(self, base_command=None):
        if base_command:
            command = base_command
        else:
            command = Command(meta={'uid': self.player.uid})

        result_cmd = command
        while True:
            # repeat until no action left
            # result_cmd = self.action_permutation(permutations, result_cmd)
            rnd_action = randint(0, 1)
            if rnd_action == 0:
                result_cmd = self.play_creature_card(result_cmd) or self.play_spell_card(result_cmd) or self.card_attack_card(result_cmd) or self.card_attack_to_player(result_cmd)
            else:
                result_cmd = self.play_spell_card(result_cmd) or self.play_creature_card(result_cmd) or self.card_attack_to_player(result_cmd) or self.card_attack_card(result_cmd)

            # region old but gold
            """
            rnd_action = randint(0, 5)
            if rnd_action == 0:
                result_cmd = self.play_spell_card(result_cmd) or self.play_creature_card(
                    result_cmd) or self.card_attack_card(result_cmd)

            elif rnd_action == 1:
                result_cmd = self.play_spell_card(result_cmd) or self.card_attack_card(
                    result_cmd) or self.play_creature_card(result_cmd)

            elif rnd_action == 2:
                result_cmd = self.play_creature_card(result_cmd) or self.play_spell_card(
                    result_cmd) or self.card_attack_card(result_cmd)

            elif rnd_action == 3:
                result_cmd = self.play_creature_card(result_cmd) or self.card_attack_card(
                    result_cmd) or self.play_spell_card(result_cmd)

            elif rnd_action == 4:
                result_cmd = self.card_attack_card(result_cmd) or self.play_creature_card(
                    result_cmd) or self.play_spell_card(result_cmd)

            elif rnd_action == 5:
                result_cmd = self.card_attack_card(result_cmd) or self.play_spell_card(
                    result_cmd) or self.play_creature_card(result_cmd)
            """
            # endregion
            # result_cmd = self.play_card(result_cmd)
            if result_cmd:
                command = result_cmd
                # logger.info("AI> HERE MY TURN RESULT {0}".format(command.items))
            else:
                logger.info("AI> play_your_turn No more action left")
                break

        # end ai's turn
        # time.sleep(1)
        command = self.player.end_turn(base_command=command)

        # print("AI.play_your_turn", command.__dict__)
        return command

    def play_creature_card(self, command):
        # time.sleep(1)
        # find playable cards
        playable_cards = []
        for card in self.player.hand.cards:
            if card.can_go_ground() and self.find_suitable_target('ondeploy', card):  # TODO what about "must-select" on deploy?
                playable_cards.append(card)

        if len(playable_cards):
            # TODO improve this

            play_this_card = playable_cards[randint(0, len(playable_cards)-1)]  # return random playable card
            logger.info("AI> play_creature_card action:playcard {0}".format(play_this_card.title))

            slot = self.player.ground.get_available_slot()
            if slot > -1:
                logger.info("AI> play_creature_card slot picked: {0}".format(slot))
                return self.player.play_creature_card(play_this_card.uuid, slot=slot, base_command=command)
            else:
                logger.info("AI> player_creature_card no available ground slot found")
        else:
            logger.info("AI> play_creature_card no playable creatures found!")

        return None

    def card_attack_card(self, command):
        # time.sleep(1)
        from server.management.commands.game_server import game
        opponent = game.get_opposite_player(self.player.uid)
        # find attackable cards

        attackable_cards = {
            "100": [],
            "50": [],
            "10": [],
            "1": []
        }
        for card in self.player.ground.cards:
            if card.can_attack():

                for target in opponent.ground.cards:
                    # TODO check target is attackable?
                    if card.it_dies_i_live(target):
                        attackable_cards["100"].append({'attacker': card, 'target': target})

                    elif card.it_dies_i_die(target):
                        attackable_cards["50"].append({'attacker': card, 'target': target})

                    elif card.it_lives_i_live(target):
                        attackable_cards["10"].append({'attacker': card, 'target': target})

                    elif card.it_lives_i_die(target):
                        attackable_cards["1"].append({'attacker': card, 'target': target})
                    else:
                        logger.info("AI> card_attack_card rate0 attacker:{0} target:{1}".format(card.title, target.title))

        attack = None
        if len(attackable_cards["100"]):
            attack = attackable_cards["100"][randint(0, len(attackable_cards["100"])-1)]

        elif len(attackable_cards["50"]):
            attack = attackable_cards["50"][randint(0, len(attackable_cards["50"])-1)]

        elif len(attackable_cards["10"]):
            attack =  attackable_cards["10"][randint(0, len(attackable_cards["10"])-1)]

        elif len(attackable_cards["1"]):
            attack =  attackable_cards["1"][randint(0, len(attackable_cards["1"])-1)]

        if attack:
            logger.info("AI> card_attack_card Attacker: {0} Target: {1}".format(attack['attacker'].title, attack['target'].title))
            return self.player.card_attack_from_ground(attack['attacker'].uuid, attack['target'].uuid, base_command=command)
        else:
            logger.info("AI> card_attack_card no more attacking available!")
        return None

    def play_spell_card(self, command):
        # time.sleep(1)
        from server.card import Card
        from server.player import Player
        playable_cards = []
        for card in self.player.hand.cards:
            targets = self.find_suitable_target('onplay', card)
            if isinstance(targets, list):
                target = targets[randint(0, len(targets)-1)]

                if card.is_spell() and card.ami_glowing():
                    target_uuid = None
                    if target:
                        if isinstance(target, Card):
                            target_uuid = target.uuid
                        elif isinstance(target, Player):
                            target_uuid = None  # TODO check this

                    playable_cards.append({
                        'from': card.uuid,
                        'target': target_uuid
                    })

        if len(playable_cards):
            play_this_card = playable_cards[randint(0, len(playable_cards)-1)]
            target_title = None
            if play_this_card['target']:
                target_title = play_this_card['target']

            logger.info("AI> play_spell_card from:{0} target:{1}".format(play_this_card['from'], target_title))

            return self.player.play_spell_card(play_this_card['from'], play_this_card['target'], base_command=command)
        else:
            logger.info("AI> play_spell_card  no target")
        return None

    def card_attack_to_player(self, command):
        # time.sleep(1)
        from server.management.commands.game_server import game
        opponent = game.get_opposite_player(self.player.uid)
        attacker_uuid = None
        target_uid = opponent.uid
        for card in self.player.ground.cards:
            if card.can_attack():
                attacker_uuid = card.uuid
                # print("THIS MUDAFUKA GOING TO ATTACK TO PLAYER target-player:", target_uid, "attacker", attacker_uuid, "goundCards:", self.player.ground.cards)
                break
        if attacker_uuid:
            return self.player.card_attack_to_player(attacker_uuid, target_uid, base_command=command)
        else:
            logger.info("AI> card_attack_to_player no more attacking available!")
        return None

    def find_suitable_target(self, for_what, from_card):
        spell = None
        for spell_item in from_card.spells:
            if spell_item.trigger == for_what:
                spell = spell_item
                logger.info("AI> find_suitable_target card.{0} found target_key: {1}".format(spell_item.trigger,
                                                                                             spell_item.target_key))
                break

        if spell:
            if "selected" in spell.target_key:
                # print(">>>", spell.target_key)
                spell.target_key = spell.target_key.replace("selected", "random")
            elif "adjacent" in spell.target_key:
                return True

            targets = spell.find_target()
            if len(targets):
                return targets
            else:
                if for_what == "ondeploy" and spell.type != "damage":  # TODO check spell type - if its damage > must select, hp/dp/hpdp not required to have a target
                    return True

                return False
        return True

    def action_permutation(self, permutations, cmd):
        luck = randint(0, len(permutations) - 1)
        permutation = permutations[luck]

        logger.info("AI> Lucky Permitation: {0}".format(permutation))

        if permutation == "play_spell:play_creature:attack_card:attack_player":
            cmd = self.play_spell_card(cmd) or self.play_creature_card(cmd) or self.card_attack_card(cmd) or self.card_attack_to_player(cmd)
        elif permutation == "play_spell:play_creature:attack_player:attack_card":
            cmd = self.play_spell_card(cmd) or self.play_creature_card(cmd) or self.card_attack_to_player(cmd) or self.card_attack_card(cmd)
        elif permutation == "play_spell:attack_card:play_creature:attack_player":
            cmd = self.play_spell_card(cmd) or self.card_attack_card(cmd) or self.play_creature_card(cmd) or self.card_attack_to_player(cmd)
        elif permutation == "play_spell:attack_card:attack_player:play_creature":
            cmd = self.play_spell_card(cmd) or self.card_attack_card(cmd) or self.card_attack_to_player(cmd) or self.play_creature_card(cmd)
        elif permutation == "play_spell:attack_player:play_creature:attack_card')":
            cmd = self.play_spell_card(cmd) or self.card_attack_to_player(cmd) or self.play_creature_card(cmd) or self.card_attack_card(cmd)
        elif permutation == "play_spell:attack_player:attack_card:play_creature":
            cmd = self.play_spell_card(cmd) or self.card_attack_to_player(cmd) or self.card_attack_card(cmd) or self.play_creature_card(cmd)
        elif permutation == "play_creature:play_spell:attack_card:attack_player":
            cmd = self.play_creature_card(cmd) or self.play_spell_card(cmd) or self.card_attack_card(cmd) or self.card_attack_to_player(cmd)
        elif permutation == "play_creature:play_spell:attack_player:attack_card":
            cmd = self.play_creature_card(cmd) or self.play_spell_card(cmd) or self.card_attack_to_player(cmd) or self.card_attack_card(cmd)
        elif permutation == "play_creature:attack_card:play_spell:attack_player":
            cmd = self.play_creature_card(cmd) or self.card_attack_card(cmd) or self.play_spell_card(cmd) or self.card_attack_to_player(cmd)
        elif permutation == "play_creature:attack_card:attack_player:play_spell":
            cmd = self.play_creature_card(cmd) or self.card_attack_card(cmd) or self.card_attack_to_player(cmd) or self.play_spell_card(cmd)
        elif permutation == "play_creature:attack_player:play_spell:attack_card":
            cmd = self.play_creature_card(cmd) or self.card_attack_to_player(cmd) or self.play_spell_card(cmd) or self.card_attack_card(cmd)
        elif permutation == "play_creature:attack_player:attack_card:play_spell":
            cmd = self.play_creature_card(cmd) or self.card_attack_to_player(cmd) or self.card_attack_card(cmd) or self.play_spell_card(cmd)
        elif permutation == "attack_card:play_spell:play_creature:attack_player":
            cmd = self.card_attack_card(cmd) or self.play_spell_card(cmd) or self.play_creature_card(cmd) or self.card_attack_to_player(cmd)
        elif permutation == "attack_card:play_spell:attack_player:play_creature":
            cmd = self.card_attack_card(cmd) or self.play_spell_card(cmd) or self.card_attack_to_player(cmd) or self.play_creature_card(cmd)
        elif permutation == "attack_card:play_creature:play_spell:attack_player":
            cmd = self.card_attack_card(cmd) or self.play_creature_card(cmd) or self.play_spell_card(cmd) or self.card_attack_to_player(cmd)
        elif permutation == "attack_card:play_creature:attack_player:play_spell":
            cmd = self.card_attack_card(cmd) or self.play_creature_card(cmd) or self.card_attack_to_player(cmd) or self.play_spell_card(cmd)
        elif permutation == "attack_card:attack_player:play_spell:play_creature":
            cmd = self.card_attack_card(cmd) or self.card_attack_to_player(cmd) or self.play_spell_card(cmd) or self.play_creature_card(cmd)
        elif permutation == "attack_card:attack_player:play_creature:play_spell":
            cmd = self.card_attack_card(cmd) or self.card_attack_to_player(cmd) or self.play_creature_card(cmd) or self.play_spell_card(cmd)
        elif permutation == "attack_player:play_spell:play_creature:attack_card":
            cmd = self.card_attack_to_player(cmd) or self.play_spell_card(cmd) or self.play_creature_card(cmd) or self.card_attack_card(cmd)
        elif permutation == "attack_player:play_spell:attack_card:play_creature":
            cmd = self.card_attack_to_player(cmd) or self.play_spell_card(cmd) or self.card_attack_card(cmd) or self.play_creature_card(cmd)
        elif permutation == "attack_player:play_creature:play_spell:attack_card":
            cmd = self.card_attack_to_player(cmd) or self.play_creature_card(cmd) or self.play_spell_card(cmd) or self.card_attack_card(cmd)
        elif permutation == "attack_player:play_creature:attack_card:play_spell":
            cmd = self.card_attack_to_player(cmd) or self.play_creature_card(cmd) or self.card_attack_card(cmd) or self.play_spell_card(cmd)
        elif permutation == "attack_player:attack_card:play_spell:play_creature":
            cmd = self.card_attack_to_player(cmd) or self.card_attack_card(cmd) or self.play_spell_card(cmd) or self.play_creature_card(cmd)
        elif permutation == "attack_player:attack_card:play_creature:play_spell":
            cmd = self.card_attack_to_player(cmd) or self.card_attack_card(cmd) or self.play_creature_card(cmd) or self.play_spell_card(cmd)

        return cmd
