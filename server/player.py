from server.hand import Hand
from server.deck import Deck
from server.graveyard import Graveyard
from server.ground import Ground
from server.command import Command
from server.turn import Turn
from server.ai import AI
from app.settings import logger, simple_logger


class Player(object):
    websocket = None
    game = None
    uid = None
    name = None
    deck = None
    hand = None
    ground = None
    graveyard = None
    turn = None
    ai = None
    hp = 30
    inspector = False

    def __init__(self, game, is_ai=False, ai_deck_id=None, use_this_deck=None):
        self.uid = "ai"
        self.game = game

        if is_ai:
            self.name = "AI"
            self.deck = Deck(self)
            self.hand = Hand(self)
            self.ground = Ground(self)
            self.graveyard = Graveyard(self)
            self.turn = Turn(self)
            self.ai = AI(self)

            # TODO make deck for ai, for now user id=2 is an ai
            from server.models import Player as DbPlayerr, Deck as DBDeckk
            db_player = DbPlayerr.objects.get(pk=2)

            if use_this_deck:
                ai_deck = use_this_deck
            elif ai_deck_id:
                ai_deck = DBDeckk.objects.get(pk=ai_deck_id)
            else:
                ai_deck = db_player.first_deck

            for db_card in ai_deck.get_cards(randomize=True):
                card = db_card.to_virtual(self)
                self.deck.add(card)

    def __str__(self):
        return "<Player.{0} {1}>".format(self.uid, self.name)

    def __repr__(self):
        return "<Player {0}>".format(self.uid)

    def __getstate__(self):
        return {
            'uid': self.uid,
            'name': self.name,
            'deck': self.deck,
            'hand': self.hand,
            'ground': self.ground,
            'graveyard': self.graveyard,
            'turn': self.turn,
            'ai': self.ai
        }

    def start_turn(self, base_command=None):
        logger.info("################################################## STARTING TURN {0} FOR {1}".format(self.turn.no, self.uid))

        simple_logger.debug("\nTurn {0} started for {1}".format(self.turn.no, self.name))

        if self.inspector and self.game.over:
            print("Game Over")
            simple_logger.debug("\nRESULT:")
            simple_logger.debug(base_command.items)
            return base_command
            # raise Exception("Game Over")

        self.turn.start()

        if base_command:
            command = base_command
        else:
            command = Command(meta={'uid': self.uid})

        command.add('turn-begin', self.turn.to_json())

        # add draw card command
        # command = self.draw_card(base_command=command)
        result = self.draw_card(return_tailored=True)
        if result:
            if "drawed" in result:
                card = self.hand.get_card_by_uuid(result['drawed']['uuid'])

                tailored = card.cast_spell('ondraw', {'provided': card})  # returns list

                if tailored:
                    result = [result]
                    result += tailored
                    command.add('list', result)

                else:
                    command.add('drawed', result['drawed'])
                    # print(command.items)
                    # import sys
                    # sys.exit(2)
            else:
                command.add('discarded', result['discarded'])

        if self.uid == "ai" or self.inspector:
            command = self.ai.play_your_turn(base_command=command)

        opponent = self.game.get_opposite_player(self.uid)
        tailored2 = self.trigger_turn_event("onplayer:turn:begin", opponent)
        if len(tailored2):
            command.add('list', tailored2)

        """
        tailored1 = []
        opponent = self.game.get_opposite_player(self.uid)
        for card in opponent.ground.cards:
            tailored1 += card.cast_spell("onplayer:turn:end")

        logger.info("Events> player({0}):turn:end {1}".format(opponent.uid, tailored1))
        if len(tailored1):
            command.add('list', tailored1)
        """

        return command

    def end_turn(self, base_command=None):
        # logger.info("############################ ENDING TURN FOR {0}".format(self.uid))
        if not base_command:
            command = Command(meta={'uid': self.uid})
        else:
            command = base_command

        opponent = self.game.get_opposite_player(self.uid)

        tailored1 = self.trigger_turn_event("onturn:end", opponent)
        if len(tailored1):
            command.add('list', tailored1)

        tailored2 = self.trigger_turn_event("onplayer:turn:end", opponent)
        if len(tailored2):
            command.add('list', tailored2)

        logger.info("################################################## TURN ENDED FOR {0}".format(self.uid))

        return opponent.start_turn(base_command=command)

    def draw_card(self, amount=1, base_command=None, return_tailored=False):
        command = None
        if not return_tailored:
            if base_command:
                command = base_command
            else:
                command = Command(meta={'uid': self.uid})

        if len(self.deck.cards):
            card = self.deck.cards.pop()
            """ :type card: server.Card """

            deck_count = len(self.deck.cards)

            if card:
                if len(self.hand.cards) + 1 > self.hand.limit:

                    logger.info("Player> Discard card -> hand is full")
                    if return_tailored:
                        command = {'discarded': {
                            'uuid': card.uuid,
                            'uid': self.uid,
                            'ckey': card.key,
                            'deck_count': deck_count
                        }}
                    else:
                        command.add('discarded', {
                            'uuid': card.uuid,
                            'uid': self.uid,
                            'ckey': card.key,
                            'deck_count': deck_count
                        })

                else:
                    self.hand.add(card)


                    draw_data = {
                        'uid': self.uid,
                        'uuid': card.uuid,
                        'ckey': card.key,
                        'deck_count': deck_count
                    }

                    if card.is_hp_increased():  # karamurat etc
                        draw_data['hp_increased'] = True
                        draw_data['hp'] = card.hp

                    if card.is_dp_increased():  # karamurat etc
                        draw_data['dp_increased'] = True
                        draw_data['dp'] = card.dp

                    if return_tailored:
                        command = {'drawed': draw_data}
                    else:
                        command.add('drawed', draw_data)

                    simple_logger.debug("{0} drawed {1}".format(self.name, card.label))
                    logger.info("Player.{0}.draw_card {1}".format(self.uid, card.label))

            else:
                logger.info("Player> Draw failed, no cards in deck!")
        return command

    def play_creature_card(self, card_uuid, target=None, slot=4, base_command=None):

        card = self.hand.get_card_by_uuid(card_uuid)
        if not card:
            logger.info("ERROR> play_creature_card probably double playing.")
            logger.info("Player.play_creature_card uid:{0} card:{1} hand:{2}".format(
                self.uid,
                card_uuid,
                [{'uuid': c.uuid, 'title': c.title} for c in self.hand.cards]
            ))
            return None

        if base_command:
            command = base_command
        else:
            command = Command(meta={'uid': self.uid})

        # TODO check is playable?
        self.hand.remove(card)

        # TODO check is groundable?
        self.ground.add(card, slot=slot)  # ground_slot is defining here

        simple_logger.debug("{0} played creature {1}".format(self.name, card.title))

        self.turn.remaining_mana -= card.mana

        command.add('creature_card_played', {'uid': self.uid, 'uuid': card.uuid, 'slot': card.slot_index,
                                             'remaining_mana': self.turn.remaining_mana})

        tailored = card.cast_spell('ondeploy', {'provided': target})

        died = None
        if tailored and len(tailored):
            died_index = -1
            for index, item in enumerate(tailored):
                try:
                    if list(item.keys())[0] == "card_died":
                        died_index = index
                        break
                except AttributeError as err:
                    print("play_creature_card AttributeError", err, item, tailored)
            if died_index >= 0:
                died = list(tailored[died_index].values())[0]
                del tailored[died_index]

        if len(tailored):
            command.add('list', tailored)

        event_result = self.game.events.fire('onauraPlay', {'card': card, 'target': target})
        if event_result and len(event_result):
            command.add('list', event_result)

        if died:
            simple_logger.debug("{0} play_creature_card some card died {1}".format(self.name, died))
            command.add('card_died', died)

        return command

    def play_spell_card(self, attacker_uuid, target_uuid=None, base_command=None):
        cast_data = None
        target = None
        from_card = self.hand.get_card_by_uuid(attacker_uuid)
        if not from_card:
            logger.info("ERROR> play_spell_card probably double playing.")
            logger.info("Hand.DoesNotExist owner:{0} uuid:{1} hand{2}".format(
                self.uid, attacker_uuid,
                [{'title': c.title, 'uuid': c.uuid} for c in self.hand.cards]
            ))
            return None

        if target_uuid:
            if target_uuid.startswith("{0}-".format(self.uid)):  # am i targeting one of my cards?
                target_player = self
            else:
                target_player = self.game.get_opposite_player(self.uid)

            target = target_player.ground.get_card_by_uuid(target_uuid)
            cast_data = {'provided': target}

        self.hand.remove(from_card)
        self.graveyard.add(from_card)

        simple_logger.debug("{0} played spell card {1}".format(self.name, from_card.title))

        self.turn.remaining_mana -= from_card.mana

        if base_command:
            command = base_command
        else:
            command = Command(meta={'uid': self.uid})

        result_dict = {'uid': self.uid, 'uuid': from_card.uuid, 'remaining_mana': self.turn.remaining_mana,
                       'from': from_card.title}
        if target_uuid:
            result_dict['target'] = target_uuid
            result_dict['to'] = target.title

            # we assume spell cards has only one spell in it and it's trigger is onplay right?
            spell = from_card.spells[0]
            if spell.animation:
                result_dict['animation'] = spell.animation

        command.add('spell_card_played', result_dict)

        tailored = from_card.cast_spell("onplay", cast_data)  # TODO put animation type (ex: fireball, freeze etc to use in client-side)
        died = None
        if tailored:

            died_index = -1
            for index, item in enumerate(tailored):
                if list(item.keys())[0] == "card_died":
                    died_index = index
                    break

            if died_index >= 0:
                died = list(tailored[died_index].values())[0]
                del tailored[died_index]

        command.add('list', tailored)

        event_result = self.game.events.fire('onauraPlay', {'card': from_card, 'target': target})
        if event_result and len(event_result):
            command.add('list', event_result)

        if died:
            simple_logger.debug("{0} play_spell_card some card died {0}".format(self.name, died))
            command.add('card_died', died)

        return command

    def card_attack_from_ground(self, attacker_uuid, target_uuid, base_command=None):  # TODO stop attacking multiple times in one turn
        target_player = self.game.get_opposite_player(self.uid)

        attacker = self.ground.get_card_by_uuid(attacker_uuid)
        try:
            target = target_player.ground.get_card_by_uuid(target_uuid)
        except Exception as err:
            import sys
            print("{0}.ground.get_card_by_uuid({1}) DoesNotExist {1}".format(self.name, target_uuid, target_player.ground.cards))
            sys.exit(1)

        attacker.attacked_this_turn = True

        defender = None
        defenders = target_player.ground.get_cards({'defender': True, 'count': 1, 'random': True, 'exclude': target, 'ignore-immune': True})
        if len(defenders):
            defender = defenders[0]
            target = defender

        if not target:
            import sys
            print("card_attack_from_ground: NoTargetAtSecond me:{0} target:{1} {2}".format(self.name, target_uuid, target_player.ground.cards))
            sys.exit(1)

        try:
            attacker.hp -= target.dp
        except AttributeError as err:
            print("card_attack_from_ground: AttributeError.1", err, attacker.label, target, target_uuid)

        try:
            target.hp -= attacker.dp
        except AttributeError as err:
            print("card_attack_from_ground: AttributeError.2", err, target.label, attacker.label, target_uuid)

        # self.turn.remaining_mana -= attacker.mana

        if base_command:
            command = base_command
        else:
            command = Command(meta={'uid': self.uid})

        if defender:
            command.add('dummy', {'uid': target_player.uid, 'uuid': defender.uuid, 'textanim': {'text': "Defender", 'harmful': False}})

        # TOGETHER
        target_total_damage = attacker.dp
        attack_together = False
        if attacker.together:
            partners = self.ground.get_cards({'canattack': True, 'random': True, 'count': 1, 'exclude': attacker, 'ignore-immune': True})
            if len(partners):
                partner = partners[0]

                if target.hp > 0:  # target must be still alive after attacker's attack

                    partner.hp -= target.dp
                    target.hp -= partner.dp

                    command.add('dummy', {'uid': self.uid, 'uuid': partner.uuid, 'textanim': {'text': "Together", 'harmful': False}})

                    tailored = list()

                    tailored.append({
                        'attacked': {
                            'attacker': {'uid': self.uid, 'uuid': attacker.uuid, 'attacked_this_turn': True},
                            'target': {'uid': target_player.uid, 'uuid': target.uuid}
                        }
                    })

                    tailored.append({
                        'attacked': {
                            'attacker': {'uid': self.uid, 'uuid': partner.uuid},
                            'target': {'uid': target_player.uid, 'uuid': target.uuid}
                        }
                    })
                    command.add('list', tailored)
                    attack_together = True
                    target_total_damage += partner.dp

        if not attack_together:
            command.add('attacked', {
                'attacker': {'uid': self.uid, 'uuid': attacker.uuid, 'attacked_this_turn': True},
                'target': {'uid': target_player.uid, 'uuid': target.uuid}
            })

        simple_logger.debug("{0} attacked to {1}".format(attacker.label, target.label))

        tailor1 = list()
        if target.dp > 0:
            tailor1.append({'dummy': {'uid': self.uid, 'uuid': attacker.uuid, 'textanim': {
                'text': "-{0}".format(target.dp), 'harmful': True}}})
        if target_total_damage > 0:
            tailor1.append({'dummy': {'uid': target_player.uid, 'uuid': target.uuid, 'textanim': {
                'text': "-{0}".format(target_total_damage), 'harmful': True}}})

        command.add('list', tailor1)

        tailor2 = list()
        # if attacker.is_hp_decreased():
        if target.dp > 0:  # if its bleeding
            tailor2.append({"hp_decreased": {'uid': self.uid, 'uuid': attacker.uuid, 'hp': attacker.hp}})

        # if target.is_hp_decreased():
        if target_total_damage > 0:  # if its bleeding
            tailor2.append({"hp_decreased": {'uid': target_player.uid, 'uuid': target.uuid, 'hp': target.hp}})

        # victim's defense triggering
        event_result1 = self.game.events.fire('onauraDefense', {'triggerer': target, 'attacker': attacker, 'victim': target})
        if event_result1:
            tailor2 += event_result1

        # attacker's attack triggering
        event_result2 = self.game.events.fire('onauraAttack', {'triggerer': attacker, 'attacker': attacker, 'victim': target})
        if event_result2:
            tailor2 += event_result2

        # target's ondefense triggering
        event_result3 = target.cast_spell('ondefense', {'provided': attacker})
        if event_result3:
            tailor2 += event_result3

        if len(tailor2):
            command.add('list', tailor2)

        tailor3 = []
        tailor4 = []
        if target.alive and target.hp <= 0:
            card_died_dict = {"card_died": {'uid': target_player.uid, 'uuid': target.uuid}}

            if target.avengeme and attacker.hp > 0 and len(target_player.ground.cards) - 1:  # avengeme card still on the ground
                card_died_dict['card_died']['textanim'] = {'text': "Avenge Me!", 'harmfull': True}

            tailor3.append(card_died_dict)

            event_result = target.kill(destroyer=attacker)  # trigger game event/auras
            if event_result:
                tailor4 += event_result

        if attacker.alive and attacker.hp <= 0:
            tailor3.append({"card_died": {'uid': self.uid, 'uuid': attacker.uuid}})

            event_result = attacker.kill(destroyer=target)  # trigger game event/auras
            if event_result:
                tailor4 += event_result

        if len(tailor3):  # card_died tailors
            command.add('list', tailor3)

        if len(tailor4):  # ondestroy game event
            command.add('list', tailor4)

        # target has avenge me
        if target.avengeme and target.hp <= 0 and attacker.hp and len(target_player.ground.cards):
            # TODO find most powerfull ally
            cards = target_player.ground.get_cards({'canattack': True,'random': True, 'count': 1, 'ignore-immune': True})
            if len(cards):
                avenger = cards[0]
                command.add('dummy', {'uid': target_player.uid, 'uuid': avenger.uuid, 'textanim': {'text': "Avenger", 'harmful': False}})
                command = target_player.card_attack_from_ground(avenger.uuid, attacker.uuid, base_command=command)

        # target has revenge
        if target.revenge and target.hp > 0 and target.dp > 0 and attacker.hp > 0:
            target.dp += target.revenge
            command.add('dp_increased', {'uid': target_player.uid, 'uuid': target.uuid, 'dp': target.dp, 'textanim': {'text': "Revenge", 'harmful': False}})
            command = target_player.card_attack_from_ground(target.uuid, attacker.uuid, base_command=command)

            target.dp -= target.revenge
            if target.hp > 0:  # if still alive after revenge > restore dp
                command.add('dp_restored', {'uid': target_player.uid, 'uuid': target.uuid, 'dp': target.dp})


        return command

    def card_attack_to_player(self, attacker_uuid, target_uid, base_command=None):
        if base_command:
            command = base_command
        else:
            command = Command(meta={'uid': self.uid})

        target_player = self.game.get_player_by_uid(target_uid)
        attacker_player = self.game.get_opposite_player(target_uid)
        attacker = attacker_player.ground.get_card_by_uuid(attacker_uuid)

        attacker.attacked_this_turn = True


        # DEFENDER
        defenders = target_player.ground.get_cards({'defender': True, 'count': 1, 'random': True, 'ignore-immune': True})
        if len(defenders):
            defender = defenders[0]
            command.add('dummy', {'uid': target_player.uid, 'uuid': defender.uuid,
                                  'textanim': {'text': "Defender", 'harmful': False}})
            return self.card_attack_from_ground(attacker_uuid, defender.uuid, base_command=command)

        # attacker.hp -= target.dp  TODO Player.dp not implemented yet
        target_player.hp -= attacker.dp




        target_total_damage = attacker.dp
        # TODO TOGETHER - shoul we implement attack together to player?

        simple_logger.debug("{0} attacked to player {1}({2})".format(attacker.label, target_player.name, target_player.hp))

        command.add('attacked', {
            'attacker': {'uid': self.uid, 'uuid': attacker.uuid, 'attacked_this_turn': True},
            'target': {'uid': target_player.uid}  # we don't send uuid so client must understand it's an attack to a player
        })

        tailor1 = list()
        tailor1.append({'dummy': {'uid': target_player.uid, 'textanim': {'text': "-{0}".format(target_total_damage), 'harmful': True}}})
        # TODO player's cannot attack now
        # tailor1.append({'dummy': {'uid': self.uid, 'uuid': attacker.uuid, 'textanim': {'text': "-{0}".format(target.dp), 'harmful': True}}})

        tailor1.append({"hp_decreased": {'uid': target_player.uid, 'hp': target_player.hp}})

        command.add('list', tailor1)

        # attacker's attack triggering
        event_result2 = self.game.events.fire('onauraAttack',
                                              {'triggerer': attacker, 'attacker': attacker, 'victim': target_player})
        if event_result2:
            command.add('list', event_result2)

        if target_player.hp <= 0:
            self.game.over = True
            command.add('player_died', {'uid': target_player.uid})

        # TODO if attacker died (player must have dp for this)

        return command

    def trigger_turn_event(self, trigger_key, opponent):
        tailored = []
        all_cards = self.ground.cards + opponent.ground.cards

        if "onplayer" in trigger_key or "onopponent" in trigger_key:
            trigger = "{0}:{1}".format(trigger_key, self.uid)  # TODO trigger with turn no
        else:
            trigger = trigger_key  # do not append uid at the end of the trigger key when it is "each turn begin/end"

        for card in all_cards:
            txt = ""
            for spl in card.spells:
                # logger.info(
                #    "Player> Card:[{0}'s {1}] Spell:{2} Trigger:{3} Required:{4}".format(card.player.uid, card.title,
                #                                                                         spl.type, spl.trigger,
                #                                                                         trigger))
                if spl.trigger == trigger:
                    txt += "\nEVREKAAAAAAAAAAAAAAAAAAAAA {0} owner: {1}".format(spl.trigger, card.player.uid)
                else:
                    txt += "\nNope required:{0} has:{1} player:{2} card:{3}".format(trigger, spl.trigger,
                                                                                    card.player.uid, card.title)

            if len(card.spells):
                # logger.info("Events> Bu: {0}".format(txt))
                tailored += card.cast_spell(trigger)  # my opponent's turns is ended

        # logger.info("Events> {0} {2}".format(trigger,opponent.uid, tailored))
        return tailored
