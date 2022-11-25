import asyncio
import json
import logging
import os
import queue

import uvicorn
from fastapi import FastAPI, Request, WebSocket
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp

from commands.wallpaper import wallpaper_command_handler

SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
SIGNING_SECRET = os.environ.get('SIGNING_SECRET')

logging.basicConfig(level=logging.DEBUG)

app = AsyncApp(token=SLACK_TOKEN, signing_secret=SIGNING_SECRET)
app_handler = AsyncSlackRequestHandler(app)


@app.event("app_mention")
async def handle_app_mentions(body, say, logger):
    logger.info(body)
    await say("What's up?")


# todo move to managers
queue_picture_query_shared = queue.Queue()
picture_results_shared = {}


@app.command("/new_wallpaper")
async def get_new_wallpaper(ack, respond, command):
    await ack()
    picture_url = await wallpaper_command_handler()
    picture_block = [{
        "type": "image",
        "image_url": picture_url,
        "alt_text": "wallpaper"
    }]
    await respond(blocks=picture_block)


@app.command('/ping')
async def handle_ping_command(ack, respond, command):
    """Slack '/ping' command handler."""
    await ack()
    await respond("Pong")


# @app.event("message")
# async def handle_message(message, say):
#     print(message)
#     await say("Bender is here")


# Backend API
api = FastAPI()


async def get_picture(query: str) -> str:
    queue_picture_query_shared.put(query)
    await asyncio.sleep(20)
    while query not in picture_results_shared:
        await asyncio.sleep(3)
    return picture_results_shared.pop(query)


@api.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        msg = await websocket.receive_text()
        if msg == "get_query":
            if queue_picture_query_shared.empty():
                await websocket.send_text('')
                continue
            res = queue_picture_query_shared.get()
            await websocket.send_text(res)
            continue

        msg = json.loads(msg)
        query = msg['query']
        img = msg['img']
        picture_results_shared[query] = img


@api.post("/slack/events")
async def endpoint(req: Request):
    """Base event endpoint handler."""
    return await app_handler.handle(req)


@api.post("/slack/command/{command:str}")
async def commands_endpoint(req: Request, command: str):
    """Base command endpoint handler."""
    return await app_handler.handle(req)


@api.get('/ping')
def ping():
    """Ping Pong endpoint of backend."""
    return {'message': 'pong'}


if __name__ == "__main__":
    uvicorn.run('app:api', host='0.0.0.0', reload=True)
