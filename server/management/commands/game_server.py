from django.core.management.base import BaseCommand
from server.game import Game
from pprint import pprint
import asyncio
import websockets
import json
from app.settings import logger

game = Game()
game.update()


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("server is running 127.0.0.1:5678")
        start_server = websockets.serve(chat_handler, '127.0.0.1', 5678)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()


async def chat_handler(websocket, path):
    try:
        while True:
            data_str = await websocket.recv()
            data = json.loads(data_str)

            logger.info("< {0}: {1}".format(data['type'], data))

            result = None
            players_to_del = []

            if data['type'] == "load-cards":
                """ deprecated
                user = User.objects.get(pk=int(data['uid']))
                deck = user.decks.all().first()  # TODO this is ok when both players have same cards in their decks

                cards = []
                for card in deck.cards.all():
                    item = card.to_json(user.id)
                    cards.append(item)
                try:
                    await websocket.send(json.dumps({'type': "carddb", 'items': cards}))
                except websockets.ConnectionClosed:
                    logger.info("= user {0} has gone".format(data['uid']))
                """
            elif data['type'] == "hello-with-real":
                """
                TODO multiplayer
                game.add_player(data['uid'], websocket)

                if not game.has_player(data['uid']):
                    game.add_player(data['uid'], websocket)
                    print("player {0} has added to game".format(data['uid']))
                else:
                    player = game.get_player_by_uid(data['uid'])
                    player.websocket = websocket

                if game.is_ready():
                    result = game.build_hello_response()
                else:
                    print("waiting for opponent")
                """
            elif data['type'] == "hello-with-ai":
                game.reset()  # reset Game object
                game.add_player(data['uid'], deck_id=data['deck'], inspector=data['inspector'], websocket=websocket)

                if "dungeon" in data and "stageno" in data:
                    dungeon = game.build_dungeon(data['dungeon'], data['stageno'])
                    game.add_player("ai", ai_deck_id=dungeon.deck_dbid)
                    game.dungeon = dungeon
                    game.get_player_by_uid("ai").hp = game.dungeon.boss['hp']
                else:
                    game.add_player("ai")

                response = game.load_game()
                try:
                    await websocket.send(json.dumps(response))
                except websockets.ConnectionClosed:
                    logger.info("= user {0} has gone".format(data['uid']))

            elif data['type'] == "acknowleged":
                if data['key'] == "load-game":

                    if game.is_ai_game():
                        game.ready_players = 2  # ai always ready madafaka
                    else:
                        game.ready_players += 1
                    logger.info("load-game-ack {0}".format(game.ready_players))
                    if game.is_ready():
                        response = game.start_game()
                        try:
                            await websocket.send(json.dumps(response))
                        except websockets.ConnectionClosed:
                            logger.info("= user {0} has gone".format(data['uid']))

            elif data['type'] == "start-turn":
                player = game.get_player_by_uid(data['uid'])
                response = player.start_turn()
                if response:
                    result = response.finalize()

            elif data['type'] == "end-turn":
                player = game.get_player_by_uid(data['uid'])  # whos turn is starting
                response = player.end_turn()
                if response:
                    result = response.finalize()

            elif data['type'] == "play-creature-card":
                player = game.get_player_by_uid(data['uid'])
                response = player.play_creature_card(data['uuid'], slot=data['slot'], target=data['target'])
                if response:
                    result = response.finalize()

            elif data['type'] == "play-spell-card":
                player = game.get_player_by_uid(data['uid'])
                response = player.play_spell_card(data['uuid'], data['target'])
                if response:
                    result = response.finalize()

            elif data['type'] == "card-attack-from-ground":
                player = game.get_player_by_uid(data['uid'])
                response = player.card_attack_from_ground(data['attacker'], data['target'])
                if response:
                    result = response.finalize()

            elif data['type'] == "card-attack-to-player":
                player = game.get_player_by_uid(data['uid'])
                response = player.card_attack_to_player(data['attacker'], data['target'])
                if response:
                    result = response.finalize()

            elif data['type'] == "draw-a-card":
                player = game.get_player_by_uid(data['uid'])
                response = player.draw_card()
                if response:
                    result = response.finalize()

            if result:
                # logger.info("SERVER-RESPONSE: {0}".format(result))
                for player in game.players:
                    if player.inspector or player.ai is None:
                        try:
                            await player.websocket.send(json.dumps(result))
                        except websockets.ConnectionClosed:
                            players_to_del.append(player)
                            logger.info("= user {0} has gone".format(player.uid))

                for p in players_to_del:
                    game.remove_player(p)
            game.update()  # do caching

    except websockets.ConnectionClosed:
        pass
