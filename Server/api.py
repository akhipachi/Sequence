from exceptions import GameNotStarted, GameStarted, InvalidPlayer
from fastapi import FastAPI, Request
from start import Game

app = FastAPI()


@app.get("/join")
async def join(request: Request):
    ip = request.client.host
    try:
        game = Game()
        if game.started:
            raise GameStarted()
        id, port = game.join(ip)
        return {"id": id, "port": port}
    except Exception as e:
        return {"error": str(e)}


@app.get("/join/start")
async def start(request: Request):
    ip = request.client.host
    try:
        game = Game()
        l = game.start(ip)
        return {"player": l}
    except Exception as e:
        return {"error": str(e)}


@app.get("/join/end")
async def end(request: Request):
    ip = request.client.host
    try:
        game = Game()
        if ip not in game.player_ip:
            raise InvalidPlayer()
        if game.started:
            game.end()
            del game
            return "Game ended"
        else:
            raise GameNotStarted()
    except Exception as e:
        return {"error": str(e)}
