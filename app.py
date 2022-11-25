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


@app.view("")
async def handle_submission(ack, body, client, view, logger):
    # Assume there's an input block with `input_c` as the block_id and `dreamy_input`
    name = body["user"]["name"]
    views_values = view["state"]["values"]
    mood = views_values['input_mode']['mood_view_id']['selected_option']['text']['text']
    yesterday_dids = views_values['input_ytd']['yesterday_view_id']['value']
    today_dids = views_values['input_td']['today_view_id']['value']
    # Acknowledge the view_submission request and close the modal
    await ack()
    # Do whatever you want with the input data - here we're saving it to a DB
    # then sending the user a verification of their submission

    # Message to send user
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Bender {name} reports:",
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Done:*",
            }
        },
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": f"{yesterday_dids}",
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*In a mood  {mood}  to do:*",
            }
        },
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": f"{today_dids}",
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Motivation picture*",
            }
        },
        {
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": "I Need a Marg",
            },
            "image_url": "https://assets3.thrillist.com/v1/image/1682388/size/tl-horizontal_main.jpg",
            "alt_text": "marg"
        }
    ]

    # Message the user
    try:
       await client.chat_postMessage(channel='#testreports', blocks=blocks)
    except e:
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
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Bender Report\n\n"
                    }
                },
                {
                    "type": "section",
                    "block_id": "input_mode",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*How are you today?*"
                    },
                    "accessory": {
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select an item",
                            "emoji": True
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "🙂",
                                    "emoji": True
                                },
                                "value": "value-0"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "🙃",
                                    "emoji": True
                                },
                                "value": "value-1"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "🫠",
                                    "emoji": True
                                },
                                "value": "value-2"
                            }
                        ],
                        "action_id": "mood_view_id"
                    }
                },
                {
                    "type": "input",
                    "block_id": "input_ytd",
                    "label": {
                        "type": "plain_text",
                        "text": "What you done yesterday?"
                    },
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "yesterday_view_id",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Enter text"
                        }
                    }
                },
                {
                    "type": "input",
                    "block_id": "input_td",
                    "label": {
                        "type": "plain_text",
                        "text": "What you're going do today?"
                    },
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "today_view_id",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Enter text"
                        }
                    }
                }
            ]
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


if __name__ == "__main__":
    init_database(DB_PATH)
    uvicorn.run('app:api', host='0.0.0.0', reload=True)
