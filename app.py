import asyncio
import base64
import logging
import os

import uvicorn
from fastapi import FastAPI, Request, WebSocket
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp
from slack_sdk.web.async_client import AsyncWebClient
from starlette.websockets import WebSocketDisconnect

from commands.survey import leave_report, regular_report
from blocks.leave_modal import LEAVE_MODAL
from blocks.report_modal import REPORT_MODAL
from commands.wallpaper import wallpaper_command_handler
from config import DB_PATH
from db.scheme import init_database, get_cursor

SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
SIGNING_SECRET = os.environ.get('SIGNING_SECRET')

logging.basicConfig(level=logging.INFO)

app = AsyncApp(token=SLACK_TOKEN, signing_secret=SIGNING_SECRET)
app_handler = AsyncSlackRequestHandler(app)

pictures_queue = asyncio.Queue()
results_queue = asyncio.Queue()


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
async def list_secret_command(ack, respond, command):
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


@app.command('/diffusion_check')
async def handle_diffusion_check_command(ack, respond, command, client):
    """Slack '/diffusion_check' command handler."""
    await ack()
    client: AsyncWebClient
    query = command.get("text")
    if not query:
        await respond("query is empty")
    await pictures_queue.put({"query": query})
    picture_data = await results_queue.get()
    picture_name = picture_data['picture_name']
    await client.files_upload_v2(
        channel=command.get('channel_id'),
        title=query,
        filename=picture_name,
        request_file_info=False,
        file=base64.b64decode(picture_data['picture_base64']),
    )


@app.command('/ping')
async def handle_ping_command(ack, respond, command):
    """Slack '/ping' command handler."""
    await ack()
    await respond("Pong")


async def get_motivational_picture(client, query, picture_data):
    print("SAVE ANG SHOW")
    await client.files_upload_v2(
        channel='C04C8GQ680N',
        channel_id='C04C8GQ680N',
        title=query,
        filename=picture_data['picture_name'],
        request_file_info=False,
        file=base64.b64decode(picture_data['picture_base64']),
    )


@app.view("")
async def handle_submission(ack, body, client, view, logger):
    # Assume there's an input block with `input_c` as the block_id and `dreamy_input`
    # Acknowledge the view_submission request and close the modal
    logger.info("IN VIEW START")
    await ack()

    name = body["user"]["name"]
    views_values = view["state"]["values"]

    if 'reason_view_id' in views_values['input_mode']:
        query_pic = views_values['input_mode']['reason_view_id']['selected_option']['text']['text']
        blocks = leave_report(views_values, name)
    else:
        query_pic = views_values['input_td']['today_view_id']['value']
        blocks = regular_report(views_values, name)
    logger.info("GOT BLOCKS")
    # Message the user
    try:
        await pictures_queue.put({"query": query_pic})
        picture_data = await results_queue.get()
        logger.info("H1T")
        await client.chat_postMessage(channel='#bender', blocks=blocks)
        logger.info("H2")
        await get_motivational_picture(client, query_pic, picture_data)
        logger.info("H3")
    except Exception as e:
        logger.exception(f"Failed to post a message {e}")


@app.shortcut("open_modal_report")
async def open_modal(ack, shortcut, client):
    # Acknowledge the shortcut request
    await ack()
    # Call the views_open method using the built-in WebClient
    await client.views_open(
        trigger_id=shortcut["trigger_id"],
        # A simple view payload for a modal
        view={
            "type": "modal",
            "title": {"type": "plain_text", "text": "Bender Report"},
            "close": {"type": "plain_text", "text": "Close"},
            "submit": {
                "type": "plain_text",
                "text": "Submit",
            },
            "blocks": REPORT_MODAL
        }
    )


@app.shortcut("leave_modal")
async def leave_modal(ack, shortcut, client):
    # Acknowledge the shortcut request
    await ack()
    # Call the views_open method using the built-in WebClient
    await client.views_open(
        trigger_id=shortcut["trigger_id"],
        # A simple view payload for a modal
        view={
            "type": "modal",
            "title": {"type": "plain_text", "text": "Bender Leave"},
            "close": {"type": "plain_text", "text": "Close"},
            "submit": {
                "type": "plain_text",
                "text": "Submit",
            },
            "blocks": LEAVE_MODAL
        }
    )


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

@api.post("/slack/interactive-endpoint/{command:str}")
async def interactives_endpoint(req: Request, command: str):
    """Base command endpoint handler."""
    return await app_handler.handle(req)


@api.get('/ping')
def ping():
    """Ping-Pong endpoint of backend."""
    return {'message': 'pong'}


@api.websocket_route('/ws/picture_service')
async def picture_service_handle(websocket: WebSocket):
    await websocket.accept()
    print('websocket connected')
    while True:
        try:
            message: dict = await websocket.receive_json()

            if message.get('service_name') == 'picture_generator' and message.get('event') == 'request_picture':
                picture_request = await pictures_queue.get()
                await websocket.send_json(picture_request)

            if message.get('service_name') == 'picture_generator' and message.get('event') == 'response_picture':
                picture_data = message.get('picture_data')
                await results_queue.put(picture_data)
                await websocket.send_json({'ok': True})
        except WebSocketDisconnect as exc:
            print('disconnected websocket')
            break


if __name__ == "__main__":
    init_database(DB_PATH)
    uvicorn.run('app:api', host='0.0.0.0', reload=True)
