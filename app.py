import logging
import os

import uvicorn
from fastapi import FastAPI, Request
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp

from commands.wallpaper import wallpaper_command_handler
from db.scheme import init_database, get_cursor
from config import DB_PATH

SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
SIGNING_SECRET = os.environ.get('SIGNING_SECRET')

logging.basicConfig(level=logging.DEBUG)

app = AsyncApp(token=SLACK_TOKEN, signing_secret=SIGNING_SECRET)
app_handler = AsyncSlackRequestHandler(app)


@app.event("app_mention")
async def handle_app_mentions(body, say, logger):
    logger.info(body)
    await say("What's up?")


@app.command("/secret_add")
async def add_secret_command(ack, respond, command):
    await ack()
    pair = command.get("text", "").split("=")

    if len(pair) != 2:
        await respond(f"{pair} can't be parsed. Please write: KEY=VALUE")
    key, value = (i.strip() for i in pair)
    if not key or not value:
        await respond(f"{key=} {value=} can't be None")
    cur = get_cursor(DB_PATH)
    cur.execute("INSERT INTO SECRETS(key, value, chat_id) VALUES(?,?,?)", (key, value, command['channel_id']))
    res = cur.rowcount
    if res == 1:
        text = f"{key} successfully added"
    else:
        text = "something went wrong!"
    await respond(text)


@app.command("/secret_delete")
async def delete_secret_command(ack, respond, command):
    await ack()
    key = command.get("text", "").strip()

    if not key:
        await respond(f"{key=} can't be None")
    cur = get_cursor(DB_PATH)
    cur.execute("DELETE FROM SECRETS where key=(?) and chat_id=(?)", (key, command['channel_id']))
    res = cur.rowcount
    if res == 1:
        text = f"{key} successfully deleted"
    elif res == 0:
        text = f"{key} not found!"
    else:
        text = "something went wrong!"
    await respond(text)


@app.command("/secret_list")
async def delete_secret_command(ack, respond, command):
    await ack()
    cur = get_cursor(DB_PATH)
    cur.execute("SELECT key, value from secrets where chat_id=(?)", (command['channel_id'],))
    text = "\n".join([f"{key}={value}" for key, value in cur.fetchall()])
    if not text:
        text = "Storage is empty"
    await respond(text)


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
    """Ping-Pong endpoint of backend."""
    return {'message': 'pong'}


if __name__ == "__main__":
    init_database(DB_PATH)
    uvicorn.run('app:api', host='0.0.0.0', reload=True)
