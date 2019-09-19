from server.deck import Deck
from server.models import Player, Dungeon as DBDungeon
from server.player import Player as AIPlayer
from server.dungeon import Dungeon
from server.hand import Hand
from server.ground import Ground
from server.graveyard import Graveyard
from server.command import Command
from server.turn import Turn
from server.events import GameEvents
from server.ai import AI
from server import cache
from app.settings import logger, simple_logger
from random import randint


class Game(object):
    id = randint(1, 99)
    players = []
    events = GameEvents()
    ready_players = 0
    game_type = "with-ai"
    who_starts = None
    dungeon = None
    over = False

    def __init__(self):
        simple_logger.debug("\n\nGame started with id: {0}".format(self.id))

    def __getstate__(self):
        result = {
            'id': self.id,
            'players': self.players,
            'events': self.events.__dict__,
            'ready_players': self.ready_players,
            'game_type': self.game_type,
            'who_starts': self.who_starts,
            'dungeon': self.dungeon
        }
        return result

    def update(self):
        cache.set('game', self.__getstate__())
        # logger.info("cache.set('game') == {0}".format(cache.get('game')))
        # logger.info("Cache updated!")

    def is_ready(self):
        return self.ready_players == 2

    def reset(self):
        self.players = []
        self.events = GameEvents()
        self.dungeon = None
        self.id = randint(1, 99)
        self.over = False
        simple_logger.debug("\n\nGame started with id: {0}".format(self.id))

    def build_dungeon(self, dungeon_id, stage_no):
        dbdungeon = DBDungeon.objects.get(pk=dungeon_id)
        dbstage = dbdungeon.stages.get(no=stage_no)

        dungeon = Dungeon()
        dungeon.name = dbdungeon.name
        dungeon.cardback = dbdungeon.cardback_image
        dungeon.stage = stage_no
        dungeon.next_stage = dbstage.next_stage.no if dbstage.next_stage else None
        dungeon.deck_dbid = dbstage.boss_deck_id
        dungeon.boss = {
            'name': dbstage.boss_name,
            'portrait': dbstage.boss_portrait,
            'hp': dbstage.boss_hp
        }
        return dungeon

    def is_ai_game(self):
        return self.game_type == "with-ai"

    def get_nonai_player(self):
        for player in self.players:
            if player.uid != "ai":
                return player
        return None

    def get_player_by_uid(self, uid):
        for player in self.players:
            if player.uid == uid:
                return player
        return None

    def get_opposite_player(self, uid):
        return self.players[1] if self.players[0].uid == uid else self.players[0]

    def has_player(self, uid):
        for player in self.players:
            if player.uid == uid:
                return True
        return False

    def add_player(self, uid, deck_id=None, ai_deck_id=None, inspector=False, websocket=None):
        if uid == "ai":
            player = AIPlayer(game=self, is_ai=True, ai_deck_id=ai_deck_id)
        else:
            db_player = Player.objects.get(pk=uid)
            player = db_player.to_virtual(game=self)
            player.websocket = websocket
            player.inspector = inspector

            player.deck = Deck(player)
            if deck_id:
                deck = db_player.user.decks.get(pk=deck_id)
            else:
                deck = db_player.first_deck

            for db_card in deck.get_cards(randomize=True):
                card = db_card.to_virtual(player)
                player.deck.add(card)

            player.hand = Hand(player)
            player.ground = Ground(player)
            player.graveyard = Graveyard(player)
            player.turn = Turn(player)
            if inspector:
                player.ai = AI(player)
        self.players.append(player)

    def remove_player(self, player):
        self.players.remove(player)
        logger.info("Game> remove_player: {0}".format(player.uid))

    def load_game(self):
        from server.models import Card
        result = {
            'id': self.id,
            'type': 'load-game',
            'players': None,
            'carddb': [c.to_json() for c in Card.objects.all()],
            'first_cards': None
        }

        if self.dungeon:
            result['dungeon'] = {
                'name': self.dungeon.name,
                'stage': self.dungeon.stage,
                'next_stage': self.dungeon.next_stage,
                'cardback': self.dungeon.cardback,
                'boss': {
                    'name': self.dungeon.boss['name'],
                    'portrait': self.dungeon.boss['portrait'],
                    'hp': self.dungeon.boss['hp']
                }
            }

        players = []
        for player in self.players:
            # cards = [vc.to_simple_json() for vc in player.deck.cards]
            players.append({
                'uid': player.uid,
                'name': player.name,
                'deck_count': len(player.deck.cards)
            })

        result['players'] = players

        cards1 = [
            self.players[0].draw_card(return_tailored=True),
            self.players[1].draw_card(return_tailored=True)
        ]

        # drawed_cards[1][0] = self.players[1].draw_card_by_key(card_key="creature_corrupted-warmaster")

        cards2 = [
            self.players[0].draw_card(return_tailored=True),
            self.players[1].draw_card(return_tailored=True)
        ]

        cards3 = [
            self.players[0].draw_card(return_tailored=True),
            self.players[1].draw_card(return_tailored=True)
        ]

        command = Command(meta={'uid': self.players[0].uid})  # player is temp

        command.add('list', cards1)
        command.add('list', cards2)
        command.add('list', cards3)
        """
        drawed_cards = [[], []]
        j = 0
        for player in self.players:
            for i in range(3):
                if i == 0 and player.uid == "ai":
                    drawed_cards[j] += player.draw_card_by_key(card_key="creature_corrupted-warmaster")
                else:
                    drawed_cards[j] += player.draw_card(return_tailored=True)
            j += 1

        command = Command(meta={'uid': self.players[0].uid})  # player is temp

        command.add('list', [drawed_cards[0][0], drawed_cards[1][0]])
        command.add('list', [drawed_cards[0][1], drawed_cards[1][1]])
        command.add('list', [drawed_cards[0][2], drawed_cards[1][2]])
        """
        result['first_cards'] = command.finalize()
        return result

    def start_game(self):
        # self.who_starts = self.players[randint(0, 1)]
        self.who_starts = self.get_player_by_uid("ai")  # TODO
        # self.who_starts = self.get_nonai_player()
        result = {
            'type': 'start-game',
            'cmds': self.who_starts.start_turn().finalize()
        }

        return result

    def draw_first_cards(self, uid):
        # who_starts = self.players[randint(0, 1)]
        # who_starts = self.get_player_by_uid("ai")  # TODO
        who_starts = self.get_nonai_player()

        drawed_cards = [[], []]
        j = 0
        for player in self.players:
            for i in range(3):
                drawed_cards[j] += player.draw_card(return_tailored=True)
            j += 1

        result = {
            'type': "draw-first-cards",
            'who_starts': who_starts.uid,
            'cmds': []
        }

        command = Command(meta={'uid': uid})
        command.add('list', [drawed_cards[0][0], drawed_cards[1][0]])
        command.add('list', [drawed_cards[0][1], drawed_cards[1][1]])
        command.add('list', [drawed_cards[0][2], drawed_cards[1][2]])


        # command = who_starts.start_turn(base_command=command)

        result['cmds'] = command

        return result
