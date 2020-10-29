from fastapi import FastAPI, Request
from pydantic import BaseModel

from start import Game, Player


app = FastAPI()


@app.get('/join')
async def join(request: Request):
    ip = request.client.host
    game = Game()
    print(game.players)
    if game.started:
        return {'error': 'Game already started'}
    id,port = game.join(ip)
    return {'id': id,'port':port}


@app.get('/join/start')
async def start(request: Request):
    ip = request.client.host
    game = Game()
    l = game.start(ip)
    if(isinstance(l, Player)):
        return {'player': l}
    else:
        return {'error': l}


@app.get('/join/end')
async def end(request: Request):
    ip = request.client.host
    game = Game()
    if ip not in game.player_ip:
        return {'error': 'Invalid player'}
    if game.started:
        game.end()
        del game
        return 'Game ended'
    else:
        return {'error': 'game not yet started'}
