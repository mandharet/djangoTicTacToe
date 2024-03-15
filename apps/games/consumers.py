import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
from channels.db import database_sync_to_async
from django.utils import timezone
from .tic_tac_field import TicTacField, TicTacFieldSerializer
from . import models
from . import business_logic as bl
import traceback

CELL_VALUES = ['X', 'O']

def populate_message(action, message='', **kwargs):
    msg = {
        'action': action,
        'details': {'message': message},
    }
    msg['details'].update(kwargs)
    return {'text': json.dumps(msg)}

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

        await bl.handle_player_join(game_info, game)

    async def disconnect(self, close_code):
        import pdb; pdb.set_trace()
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        game_info = await bl.get_game_info()
        
        import pdb; pdb.set_trace()
        players_queue = game_info['players-queue']
        
        import pdb; pdb.set_trace()
        players = game_info['players']

        if self.channel_name in players:
            disconnected = players.pop(self.channel_name)
            players_queue.remove(self.channel_name)
            await bl.send_game_action_message(f'{disconnected["name"]} disconnected', type='disconnect')

            game_id = game_info['game-id']
            await bl.handle_game_aborted(game_info, game_id, players_queue)

        await bl.cache_game_info(game_info)

    async def receive(self, text_data):
        try:
            msg = json.loads(text_data)
            message_type = msg['type']
            game_info = await self.get_game_info()
            game = await self.get_game()

            if game.finished or game.aborted:
                return

            await bl.handle_incoming_move(text_data, game_info, game)

            await bl.cache_game_info(game_info)
        except Exception as e:
            print("error Occurred: ",e)
            traceback.print_exc()

