import logging
import os

import uvicorn
from fastapi import FastAPI, Request
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp

from commands.wallpaper import wallpaper_command_handler
from db.scheme import init_database

SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
SIGNING_SECRET = os.environ.get('SIGNING_SECRET')

logging.basicConfig(level=logging.DEBUG)

app = AsyncApp(token=SLACK_TOKEN, signing_secret=SIGNING_SECRET)
app_handler = AsyncSlackRequestHandler(app)


@app.event("app_mention")
async def handle_app_mentions(body, say, logger):
    logger.info(body)
    await say("What's up?")


@app.command("/echo")
async def repeat_text(ack, respond, command):
    """Slack '/echo' command handler."""
    await ack()
    await respond(f"{command['command']} {command.get('text', '')}")


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


@api.post("/slack/{path_:path}")
async def endpoint(req: Request):
    """Base event endpoint handler."""
    return await app_handler.handle(req)


# @api.post("/slack/command/{command:str}")
# async def commands_endpoint(req: Request, command: str):
#     """Base command endpoint handler."""
#     return await app_handler.handle(req)


@api.get('/ping')
def ping():
    """Ping Pong endpoint of backend."""
    return {'message': 'pong'}


if __name__ == "__main__":
    init_database('db.sqlite3')
    uvicorn.run('app:api', host='0.0.0.0', reload=True)
