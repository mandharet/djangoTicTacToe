import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
from channels.db import database_sync_to_async
from django.utils import timezone
from .tic_tac_field import TicTacField, TicTacFieldSerializer
from . import models
import traceback

CELL_VALUES = ['X', 'O']

def populate_message(action, message='', **kwargs):
    msg = {
        'action': action,
        'details': {'message': message},
    }
    msg['details'].update(kwargs)
    return msg

class GameConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        room = self.scope['url_route']['kwargs']['room']
        if not room:
            print("No Room found")
            return

        await self.accept()
        self.room_group_name = f"game-{room}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        self.room = room
        game_info = await self.get_or_create_game_info()
        game = await self.get_or_create_game()

        if game.finished or game.aborted:
            return

        await self.handle_player_join(game_info, game)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        game_info = await self.get_game_info()
        players_queue = game_info['players-queue']
        players = game_info['players']

        if self.channel_name in players:
            disconnected = players.pop(self.channel_name)
            players_queue.remove(self.channel_name)
            await self.send_game_action_message(f'{disconnected["name"]} disconnected', type='disconnect')

            game_id = game_info['game-id']
            await self.handle_game_aborted(game_info, game_id, players_queue)

        await self.cache_game_info(game_info)

    async def receive(self, text_data):
        try:
            msg = json.loads(text_data)
            message_type = msg['type']
            game_info = await self.get_game_info()
            game = await self.get_game()

            if game.finished or game.aborted:
                return

            await self.handle_incoming_move(text_data, game_info, game)

            await self.cache_game_info(game_info)
        except Exception as e:
            print("error Occurred: ",e)
            traceback.print_exc()

    # Utility methods

    async def get_game_info(self):
        return await database_sync_to_async(cache.get)(f"game-{self.room}", {})

    async def get_or_create_game_info(self):
        game_info = await self.get_game_info()
        game = await self.get_game()

        if 'game-id' not in game_info:
            game_info['game-id'] = game.id
            game_info['game-field'] = TicTacFieldSerializer.serialize(TicTacField.from_game(game))

        open_games = await database_sync_to_async(cache.get)('open_games', set())

        game_info.setdefault('players-queue', [])
        game_info.setdefault('players', {})

        return game_info

    async def get_game(self):
        return await database_sync_to_async(models.Game.objects.get)(pk=self.room.split('-')[-1])

    async def get_or_create_game(self):
        return await self.get_game()

    async def handle_player_join(self, game_info, game):
        if len(game_info['players-queue']) < 2:
            number = 0
            if game_info['players-queue'] and game_info['players'][game_info['players-queue'][0]]['name'] == 'Player-2':
                number = 1
            await self.handle_player_join_queue(game_info, number, game)

        else:
            await self.send_spectator_message(game_info)

        open_games = await database_sync_to_async(cache.get)('open_games', set())
        await database_sync_to_async(cache.set)('open_games', open_games)

        await self.cache_game_info(game_info)

    async def handle_player_join_queue(self, game_info, number, game):
        game_info['players-queue'].append(self.channel_name)
        number = number or len(game_info['players-queue'])
        game_info['players'][self.channel_name] = {
            'name': f'Player-{number}',
            'symbol': CELL_VALUES[number-1]
        }
        await self.send_game_action_message(f'Player-{number} join the game', type='join')

        open_games = await database_sync_to_async(cache.get)('open_games', set())
        if len(game_info['players-queue']) == 2:
            try:
                open_games.remove(game_info['game-id'])
            except KeyError:
                pass

    async def send_spectator_message(self, game_info):
        await self.send(
            text_data=await database_sync_to_async(json.dumps)(
                populate_message('warning',
                                 'You connected as a spectator',
                                 type='spectator-connected',
                                 history=await database_sync_to_async(list)(
                                     game_info['game'].move_set.values('id', 'x', 'y')
                                 )
                                 )))

    async def handle_game_aborted(self, game_info, game_id, players_queue):
        open_games = await database_sync_to_async(cache.get)('open_games', set())
        try:
            open_games.remove(game_info['game-id'])
            open_games = await database_sync_to_async(cache.set)('open_games', open_games)
        except KeyError:
            pass

        game = await self.get_game()
        game.aborted = True
        await database_sync_to_async(game.save())

        await self.send_game_action_message(f'{game_info["players"][players_queue[0]]["name"]} win the game',
                                            type='game-aborted',
                                            winner=game_info['players'][players_queue[0]]["name"]
                                            )

    async def handle_incoming_move(self, text_data, game_info, game):
        if len(game_info['players-queue']) < 2:
            await self.send_game_action_message('Waiting for the other player...', type='warning')
            return

        if game_info['players-queue'][0] != self.channel_name:
            await self.send_game_action_message('Wrong player', type='warning')
            return
        
        msg = json.loads(text_data)
        field = TicTacFieldSerializer.restore(game_info['game-field'])
        players_queue = game_info['players-queue']
        players = game_info['players']

        x, y = int(msg['details']['x']), int(msg['details']['y'])
        if not field.get_cell(x, y):
            await self.handle_valid_move(field, x, y, game_info, players_queue, players, msg)

    async def handle_valid_move(self, field, x, y, game_info, players_queue, players, msg):
        field.set_cell(x, y, players[self.channel_name]['symbol'])
        await self.save_move_to_database(game_info['game-id'], x, y)
        await self.send_group_move_message(players_queue, players, x, y)

        win_line = field.check_lines(x, y)
        if win_line:
            await self.handle_game_winner(game_info, players_queue, players, win_line)

        players_queue.append(players_queue.pop(0))

    async def save_move_to_database(self, game_id, x, y):
        await database_sync_to_async(models.Move.objects.create)(
            game_id=game_id,
            x=x,
            y=y,
        )

    async def send_group_move_message(self, players_queue, players, x, y):
        await self.channel_layer.group_send(
            self.room_group_name,{
                'type': 'game_move',
                'message':await database_sync_to_async(populate_message)('game-action',
                                                            f'{players[players_queue[0]]["name"]} makes a move',
                                                            type='move',
                                                            x=x,
                                                            y=y,
                                                            val=players[self.channel_name]['symbol'],
                                                            player=players[players_queue[0]]["name"])
            }
        )
    
    async def game_move(self, event):
        print("sending mesg: ", event)
        await self.send(text_data=json.dumps(event['message']))

    async def handle_game_winner(self, game_info, players_queue, players, win_line):
        game_info['game-finished'] = True
        game_info['finished-time'] = timezone.now()
        game_info['finish-line'] = win_line
        await database_sync_to_async(models.Game.objects.get)(id=game_info['game-id']).save()

        await self.send_group_move_message(players_queue, players, win_line[0], win_line[1])
        await self.send_game_action_message(f'{players[players_queue[0]]["name"]} wins the game',
                                            type='game-finish',
                                            winner=players[players_queue[0]]["name"],
                                            win_line=win_line)

    async def send_game_action_message(self, message, type, **kwargs):
        await self.send(text_data=json.dumps(populate_message('game-action', message, type=type, **kwargs)))

    async def cache_game_info(self, game_info):
        await database_sync_to_async(cache.set)(f"game-{self.room}", game_info, 3600)
